# Readme

## System

- Nvidia GPU
- Cuda 12.2 (run `nvidia-smi` to find the running version)
- [Docker](https://docs.docker.com/engine/install/ubuntu/), [Post Install](https://docs.docker.com/engine/install/linux-postinstall/)
- For Docker with GPU [Nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## Install TGI from source:

- Rust `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- If on linux Install PROTOC

```
PROTOC_ZIP=protoc-21.12-linux-x86_64.zip
curl -OL https://github.com/protocolbuffers/protobuf/releases/download/v21.12/$PROTOC_ZIP
sudo unzip -o $PROTOC_ZIP -d /usr/local bin/protoc
sudo unzip -o $PROTOC_ZIP -d /usr/local 'include/*'
rm -f $PROTOC_ZIP
```

### Did not work

- `docker run --gpus all --shm-size 1g -v $PWD/model:/data ghcr.io/huggingface/text-generation-inference:1.1.0 --model-id TheBloke/Mistral-7B-Instruct-v0.2-GPTQ --revision gptq-8bit--1g-actorder_True --quantize gptq --max-input-length 3696 --max-total-tokens 4096 --max-batch-prefill-tokens 4096`
- `docker run --gpus all --shm-size 1g -v $PWD/model:/data ghcr.io/huggingface/text-generation-inference:1.3 --model-id TheBloke/Mistral-7B-Instruct-v0.2-GPTQ --revision gptq-8bit--1g-actorder_True --quantize gptq --max-input-length 3696 --max-total-tokens 4096 --max-batch-prefill-tokens 4096`

### Other options

- https://hamel.dev/notes/llm/inference/03_inference.html
- https://betterprogramming.pub/frameworks-for-serving-llms-60b7f7b23407

- https://github.com/OpenNMT/CTranslate2
- vllm
- openllm

## Running the model using transformers

- A Python 3.10 environment

```
torch==2.1.1
torchvision==0.16.1
torchaudio==2.1.1
transformers==4.36.0
optimum==1.15.0
auto-gptq==0.5.1
```
