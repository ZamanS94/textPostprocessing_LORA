from pathlib import Path
import re
from jiwer import process_words
from jiwer import wer
import os

def clean_text_transcription(text: str):
    text = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ0-9-]+", " ", text)
    text = re.sub(r"\bextra\s*id\s*\d+\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bKorjaa\s+OCR-virheet\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text

from jiwer import process_words

def calculate_wer_rates(gt_text, trans_text):
    
    out = process_words(gt_text,trans_text)
    C = out.hits
    S = out.substitutions
    D = out.deletions
    I = out.insertions

    N_ref = C + S + D
    if N_ref == 0:
        return 0.0, 0.0, 0.0, 0.0
    deleted_rate = D / N_ref * 100
    added_rate = I / N_ref * 100
    substitution_rate = S / N_ref * 100
    wer = (S + D + I) / N_ref * 100
    return wer, deleted_rate, added_rate, substitution_rate


def calculate_errors(gt_file: Path, trans_file: Path, error_report: Path):
    gt_text = Path(gt_file).read_text(encoding="utf-8")
    trans_text = Path(trans_file).read_text(encoding="utf-8")
    gt_words = clean_text_transcription(gt_text)
    trans_words = clean_text_transcription(trans_text)
    print(trans_words)
    
    print(f"Processing file: {gt_file.name}")
    print(f"GT: {len(gt_text)} chars, {len(gt_words)} words")
    print(f"Transcription: {len(trans_text)} chars, {len(trans_words)} words")

    total_gt_words = len(gt_words)
    total_trans_words = len(trans_words)

    if total_gt_words == 0 or total_trans_words == 0:
        print(f"️ Skipping {gt_file.name} due to empty GT or transcription")
        return 0, 0, 0, 0, 0, 0  # safe return

    wer, deleted_rate, added_rate, substitution_rate = calculate_wer_rates(gt_words, trans_words)

    with open(error_report, "a", encoding="utf-8") as f:
        f.write(f"File: {gt_file.name}\n")
        f.write(f"Total words in GT: {total_gt_words}\n")
        f.write(f"Total words in transcription: {total_trans_words}\n")
        print(f"WER: {wer:.2f}% | Substitution: {substitution_rate:.2f}% | Deleted: {deleted_rate:.2f}% | Added: {added_rate:.2f}%\n")
        f.write(f"WER: {wer:.2f}% | Substitution: {substitution_rate:.2f}% | Deleted: {deleted_rate:.2f}% | Added: {added_rate:.2f}%\n")
        f.write("="*40 + "\n")

    return total_gt_words, total_trans_words, wer, deleted_rate, added_rate, substitution_rate


def evaluate(gt_folder, pred_folder, report_file):
    for file_name in os.listdir(gt_folder):
        if file_name.endswith(".txt"):
            calculate_errors(
                Path(gt_folder, file_name),
                Path(pred_folder, file_name),
                report_file
            )
            
    return



if __name__ == "__main__":
    print("DEBUGGING")
    evaluate(gt_folder="/scratch/project_2010972/sabina/FineTuning/final/test_GT", pred_folder="/scratch/project_2010972/sabina/FineTuning/final/test_OUT", report_file="test.txt")
