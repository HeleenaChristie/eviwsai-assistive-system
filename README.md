# EVISWAI: Assistive System for the Visually Impaired

This repository contains the source code for **EVISWAI**, an assistive artificial intelligence system designed to support visually impaired users by converting visual and textual information into concise, meaningful audio outputs.

## Overview
The system integrates multiple AI modules to provide end-to-end assistance:

- Image Captioning using BLIP
- Optical Character Recognition (OCR) using Tesseract
- Text Summarization using a fine-tuned DistilBART model
- Text-to-Speech (TTS) conversion

The objective of EVISWAI is to address the limitations of traditional screen readers by generating context-aware and summarized audio descriptions.

## Models Used
- Fine-tuned DistilBART trained on the BBC News dataset for abstractive summarization  
- BLIP model for image caption generation  
- Tesseract OCR engine for text extraction  

## Repository Structure
├── visable.py # Main application script integrating OCR, captioning, summarization, and TTS
├── README.md # Project documentation
├── LICENSE # License file


