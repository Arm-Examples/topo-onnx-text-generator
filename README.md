# Text Generator (ONNX Runtime GenAI)

> This project is a [Topo](https://github.com/arm/topo) template and follows the [Topo Project Specification](https://github.com/arm/topo/tree/main/docs/project-specification).

An on-device evaluation harness for Arm-optimised generative ONNX models. Supply a compatible Hugging Face model, deploy it to your own Arm device, enter prompts through a web UI, and evaluate generation quality and CPU performance on your real hardware.

It demonstrates:

- A multi-stage Docker build that snapshots a Hugging Face repository into the image at build time. The deployed device needs no Hugging Face token or network access.
- A config-driven inference runner that maps each model repository's `config.yaml` to prompt processing and ONNX Runtime GenAI operations.
- Streaming output with time to first token (TTFT), decode throughput, and token counts in a Gradio interface.

## Model compatibility

The project supports ONNX Runtime GenAI repositories whose files follow the configuration patterns used by these models:

- [`Arm/gemma-3-1b-base-onnx-genai-int4-emb-int8`](https://huggingface.co/Arm/gemma-3-1b-base-onnx-genai-int4-emb-int8)
- [`Arm/gemma-3-1b-instruct-onnx-genai-int4-emb-int8`](https://huggingface.co/Arm/gemma-3-1b-instruct-onnx-genai-int4-emb-int8)
- [`Arm/llama-3-1-8b-base-onnx-genai-int4-kquantlast-emb-int8`](https://huggingface.co/Arm/llama-3-1-8b-base-onnx-genai-int4-kquantlast-emb-int8)
- [`Arm/llama-3-1-8b-instruct-onnx-genai-int4-kquantlast-emb-int8`](https://huggingface.co/Arm/llama-3-1-8b-instruct-onnx-genai-int4-kquantlast-emb-int8)
- [`Arm/llama-3-2-1b-base-onnx-genai-int4-kquantlast-emb-int8-graviton-g4`](https://huggingface.co/Arm/llama-3-2-1b-base-onnx-genai-int4-kquantlast-emb-int8-graviton-g4)
- [`Arm/llama-3-2-1b-base-onnx-genai-int4-kquantlast-emb-int8-vivo-x300`](https://huggingface.co/Arm/llama-3-2-1b-base-onnx-genai-int4-kquantlast-emb-int8-vivo-x300)
- [`Arm/llama-3-2-1b-instruct-onnx-genai-int4-kquantlast-emb-int8-graviton-g4`](https://huggingface.co/Arm/llama-3-2-1b-instruct-onnx-genai-int4-kquantlast-emb-int8-graviton-g4)
- [`Arm/llama-3-2-1b-instruct-onnx-genai-int4-kquantlast-emb-int8-vivo-x300`](https://huggingface.co/Arm/llama-3-2-1b-instruct-onnx-genai-int4-kquantlast-emb-int8-vivo-x300)
- [`Arm/llama-3-2-3b-instruct-onnx-genai-int4-kquantlast-emb-int8`](https://huggingface.co/Arm/llama-3-2-3b-instruct-onnx-genai-int4-kquantlast-emb-int8)
- [`Arm/qwen3-0-6b-onnx-genai-int4-kquantlast-emb-int4`](https://huggingface.co/Arm/qwen3-0-6b-onnx-genai-int4-kquantlast-emb-int4)
- [`Arm/tinyllama-1-1b-chat-onnx-genai-int4-kquantlast-emb-int8-graviton-g4`](https://huggingface.co/Arm/tinyllama-1-1b-chat-onnx-genai-int4-kquantlast-emb-int8-graviton-g4)
- [`Arm/tinyllama-1-1b-chat-onnx-genai-int4-kquantlast-emb-int8-vivo-x300`](https://huggingface.co/Arm/tinyllama-1-1b-chat-onnx-genai-int4-kquantlast-emb-int8-vivo-x300)

A compatible repository must contain:

- `config.yaml` with a supported `input.preprocessing` pipeline.
- `genai_config.json`, the model and its external-data sidecar, `tokenizer.json`, and `tokenizer_config.json`.
- The referenced Jinja chat template, when `config.yaml` specifies one.

The downloader snapshots the repository so that ONNX external-data sidecars and tokenizer assets are included. The 8B models produce images larger than 5 GB before runtime dependencies; ensure the build host and target have enough disk space and memory.

## Build-time parameters

The model identity is a Docker build argument, resolved at build time. There is no default.

| Parameter | Required | Description                   | Example                                              |
| --------- | -------- | ----------------------------- | ---------------------------------------------------- |
| `MODEL`   | yes      | Hugging Face model repository | `Arm/qwen3-0-6b-onnx-genai-int4-kquantlast-emb-int4` |

## Usage

The easiest deployment path is [Topo](https://github.com/arm/topo).

### Clone the project

```bash
topo clone git@github.com:Arm-Examples/topo-onnx-text-generator.git
```

Topo prompts for `MODEL` because the project has no default model.

### Build and deploy

```bash
cd topo-onnx-text-generator
export HF_TOKEN=<your-hf-read-token>
topo deploy --target <user@hostname>
```

Topo builds the image on the host where the token is available and transfers the finished image to the Arm target. The target needs neither the token nor access to Hugging Face.

### What you will see

Open `http://<ip-address-of-target>:7860`, enter a prompt, and choose **Generate**. Text streams into the interface while it reports TTFT, decode tokens per second, total latency, and prompt/output token counts.
