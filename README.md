# Text Generator (ONNX Runtime GenAI)

> This is a [Topo](https://github.com/arm/topo) Project and follows the [Topo Project Specification](https://github.com/arm/topo/tree/main/docs/project-specification).

This on-device harness evaluates Arm-optimized generative ONNX models. Supply a compatible Hugging Face model and deploy the Project to an Arm Target. Use the web interface to enter prompts and evaluate generation quality and CPU performance on the Target.

It demonstrates:

- A multi-stage Docker build that snapshots a Hugging Face repository into the image at build time. The Target needs no Hugging Face token or network access.
- A config-driven inference runner that maps `config.yaml` from each model repository to prompt processing and ONNX Runtime GenAI operations.
- Streaming output with time to first token (TTFT), decode throughput, and token counts in a Gradio interface.

## Model compatibility

A compatible repository must contain:

- `config.yaml` with a supported `input.preprocessing` pipeline.
- `genai_config.json`, the model and its external-data sidecar, `tokenizer.json`, and `tokenizer_config.json`.
- The referenced Jinja chat template, when `config.yaml` specifies one.

The 8B models produce images larger than 5 GB before runtime dependencies. Ensure that the Host and Target have enough disk space and memory.

## Project parameters

`HF_REPO_ID` and `HF_ENDPOINT` are optional Project parameters passed to the Docker build as arguments:

| Parameter     | Required | Description                   | Default                                              |
| ------------- | -------- | ----------------------------- | ---------------------------------------------------- |
| `HF_REPO_ID`  | no       | Hugging Face model repository | `Arm/qwen3-0-6b-onnx-genai-int4-kquantlast-emb-int4` |
| `HF_ENDPOINT` | no       | Hugging Face API endpoint     | `https://huggingface.co`                             |

## Usage

Install [Topo](https://github.com/arm/topo), then use it to clone and deploy the Project.

### Clone the Project

The clone step will prompt you for values for the `HF_REPO_ID` and `HF_ENDPOINT` parameters. Leave either input empty to select its default.

```bash
topo clone https://github.com/Arm-Examples/topo-onnx-text-generator.git
```

### Build and deploy the Project

```bash
cd topo-onnx-text-generator
topo deploy --target <user@hostname>
```

Topo builds the image on the Host and transfers the finished image to the Target over SSH. The Target does not need network access to download the model.

> **Note:** To download a private model at build time, set `HF_TOKEN` on the Host before running `topo deploy`. The token must have read access to the repository. The build mounts it as a secret and does not store it in the image or transfer it to the Target. Public repositories do not require a token.

### What you will see

Open `http://<target-ip>:7860`, enter a prompt, and click **Generate**. Text streams into the interface while it reports TTFT, decode tokens per second, total latency, and prompt and output token counts.
