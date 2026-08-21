# Text Generator (ONNX Runtime GenAI)

> This is a [Topo](https://github.com/arm/topo) Project and follows the [Topo Project Specification](https://github.com/arm/topo/tree/main/docs/project-specification).

This on-device harness evaluates Arm-optimized generative ONNX models. Supply a compatible Hugging Face model and deploy the Project to an Arm Target. Use the web interface to enter prompts and evaluate generation quality and CPU performance on the Target.

It demonstrates:

- A multi-stage Docker build that snapshots a Hugging Face repository into the image at build time. The Target needs no Hugging Face token or network access.
- A config-driven inference runner that maps `config.yaml` from each model repository to prompt processing and ONNX Runtime GenAI operations.
- Streaming output with time to first token (TTFT), decode throughput, and token counts in a Gradio interface.

## Model compatibility

The Project supports ONNX Runtime GenAI repositories whose files follow the configuration patterns used by these models:

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

The 8B models produce images larger than 5 GB before runtime dependencies. Ensure that the Host and Target have enough disk space and memory.

## Project parameters

`MODEL` and `HF_ENDPOINT` are optional Project parameters passed to the Docker build as arguments:

| Parameter     | Required | Description                   | Default                                              |
| ------------- | -------- | ----------------------------- | ---------------------------------------------------- |
| `MODEL`       | no       | Hugging Face model repository | `Arm/qwen3-0-6b-onnx-genai-int4-kquantlast-emb-int4` |
| `HF_ENDPOINT` | no       | Hugging Face API endpoint     | `https://huggingface.co`                             |

## Usage

Install [Topo](https://github.com/arm/topo), then use it to clone and deploy the Project.

### Clone the Project

The clone step will prompt you for values for the `MODEL` and `HF_ENDPOINT` parameters. Leave either input empty to select its default.

```bash
topo clone https://github.com/Arm-Examples/topo-onnx-text-generator.git
```

### Build and deploy the Project

```bash
cd topo-onnx-text-generator
export HF_TOKEN=<your-hf-read-token>
topo deploy --target <user@hostname>
```

Topo builds the image on the Host and transfers the finished image to the Target over SSH. The Target does not receive the token and does not need network access to download the model.

### What you will see

Open `http://<target-ip>:7860`, enter a prompt, and click **Generate**. Text streams into the interface while it reports TTFT, decode tokens per second, total latency, and prompt and output token counts.
