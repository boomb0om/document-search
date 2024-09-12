from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline


class TextCorrector:
    def __init__(self, ckpt_path: str, batch_size: int = 32, device: str = "cpu"):
        self.device = device
        self.batch_size = batch_size
        self.tokenizer = AutoTokenizer.from_pretrained(ckpt_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(ckpt_path)
        self.pipeline = pipeline(
            task="text2text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            batch_size=self.batch_size,
            device=self.device,
        )

    def __call__(self, texts: list[str]) -> list[str]:
        return [out["generated_text"] for out in self.pipeline(texts)]
