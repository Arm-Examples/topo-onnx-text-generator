"""Config-driven text generation with ONNX Runtime GenAI."""

import json
from collections.abc import Iterator
from pathlib import Path
from time import perf_counter

import onnxruntime_genai as og
import yaml
from jinja2 import Environment
from tokenizers import Tokenizer

CHAT_TEMPLATES = {
    "gemma3": (
        "{{ bos_token }}<start_of_turn>user\n{{ messages[0].content }}"
        "<end_of_turn>\n<start_of_turn>model\n"
    )
}


def _raise_exception(message: str) -> None:
    raise RuntimeError(message)


class TextGenerator:
    """Load one model directory and expose reusable generation operations."""

    def __init__(self, model_dir: str | Path):
        self.model_dir = Path(model_dir)
        config_path = self.model_dir / "config.yaml"
        config = yaml.safe_load(config_path.read_text())
        generation = config.get("generation", {})
        preprocessing = config.get("input", {}).get("preprocessing", [])
        operations = {
            name: options for step in preprocessing for name, options in step.items()
        }
        tokenize = operations.get("tokenize", {})

        self.max_length = generation.get("default_max_length", 512)
        self.default_decode_tokens = generation.get("default_decode_tokens", 60)
        self.search_options = {
            "do_sample": generation.get("do_sample", False),
            "temperature": generation.get("temperature", 0.0),
        }
        self.bos_token_id = operations.get("prepend_bos", {}).get("bos_token_id")

        self.model = og.Model(str(self.model_dir))
        self.tokenizer = Tokenizer.from_file(
            str(self.model_dir / tokenize.get("tokenizer", "tokenizer.json"))
        )
        self.add_special_tokens = tokenize.get("add_special_tokens", False)
        self.template = self._load_template(operations.get("apply_chat_template"))

    def _load_template(self, chat_config):
        if chat_config is None:
            return None

        settings = chat_config if isinstance(chat_config, dict) else {}
        template_name = settings.get("template", chat_config)
        template_source = CHAT_TEMPLATES.get(template_name)
        if template_source is None:
            template_source = (self.model_dir / template_name).read_text()

        engine_options = settings.get("engine_options", {})
        environment = Environment(
            trim_blocks=engine_options.get("trim_blocks", True),
            lstrip_blocks=engine_options.get("lstrip_blocks", True),
            autoescape=False,
        )
        environment.globals["raise_exception"] = _raise_exception

        token_config = json.loads(
            (self.model_dir / "tokenizer_config.json").read_text()
        )
        variables = {
            "bos_token": token_config.get("bos_token") or "",
            "eos_token": token_config.get("eos_token") or "",
            "add_generation_prompt": True,
            "enable_thinking": False,
        }
        variables.update(settings.get("variables", {}))
        return environment.from_string(template_source), variables

    def _encode(self, prompt: str) -> list[int]:
        if self.template:
            template, variables = self.template
            prompt = template.render(
                messages=[{"role": "user", "content": prompt}], **variables
            )

        add_special_tokens = self.add_special_tokens and not self.template
        input_ids = self.tokenizer.encode(
            prompt,
            add_special_tokens=add_special_tokens,
        ).ids
        if self.bos_token_id is not None:
            input_ids.insert(0, self.bos_token_id)
        return input_ids

    def generate(self, prompt: str) -> Iterator[tuple[str, str]]:
        """Stream generated text with on-device timing."""
        if not prompt or not prompt.strip():
            yield "", "_Enter a prompt to generate text._"
            return

        input_ids = self._encode(prompt)
        max_length = min(self.max_length, len(input_ids) + self.default_decode_tokens)
        if max_length <= len(input_ids):
            raise ValueError(f"prompt exceeds the {self.max_length}-token limit")

        params = og.GeneratorParams(self.model)
        params.set_search_options(max_length=max_length, **self.search_options)
        generator = og.Generator(self.model, params)

        started = perf_counter()
        generator.append_tokens(input_ids)
        ttft_s = None
        while not generator.is_done():
            generator.generate_next_token()
            elapsed_s = perf_counter() - started
            ttft_s = ttft_s or elapsed_s
            response_ids = list(generator.get_sequence(0))[len(input_ids) :]
            response = self.tokenizer.decode(
                response_ids, skip_special_tokens=True
            ).lstrip()
            if generator.is_done():
                response = response.rstrip()

            decode_s = max(elapsed_s - ttft_s, 0.0)
            tokens_per_second = (
                (len(response_ids) - 1) / decode_s
                if len(response_ids) > 1 and decode_s > 0
                else 0.0
            )
            stats = (
                f"**{tokens_per_second:.1f} tokens/s** decode\n\n"
                f"<sub>TTFT {ttft_s * 1000:.1f} ms · "
                f"total {elapsed_s * 1000:.1f} ms · {len(input_ids)} prompt tokens · "
                f"{len(response_ids)} generated tokens · measured on this device (CPU)</sub>"
            )
            yield response, stats
