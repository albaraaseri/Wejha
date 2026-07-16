#!/bin/bash
# Download Piper TTS models for English and Arabic from Hugging Face

set -e

echo "🔊 Downloading Piper TTS Models from Hugging Face..."
echo "===================================================="

# Create models directory
mkdir -p models/piper/en_US-lessac-medium
mkdir -p models/piper/ar_JO-kareem-medium

cd models/piper

# English model: en_US-lessac-medium
echo ""
echo "📥 Downloading English model (en_US-lessac-medium)..."

if [ ! -f "en_US-lessac-medium/en-us-lessac-medium.onnx" ] || [ $(stat -f%z "en_US-lessac-medium/en-us-lessac-medium.onnx" 2>/dev/null || echo 0) -lt 1000 ]; then
    echo "   Downloading model file (this may take a few minutes)..."
    curl -L "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx" \
         -o "en_US-lessac-medium/en-us-lessac-medium.onnx" \
         --progress-bar
    echo "   ✅ Model file downloaded"
else
    echo "   ✅ Model file already exists"
fi

if [ ! -f "en_US-lessac-medium/en-us-lessac-medium.onnx.json" ] || [ $(stat -f%z "en_US-lessac-medium/en-us-lessac-medium.onnx.json" 2>/dev/null || echo 0) -lt 100 ]; then
    echo "   Downloading config file..."
    curl -L "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json" \
         -o "en_US-lessac-medium/en-us-lessac-medium.onnx.json"
    echo "   ✅ Config file downloaded"
else
    echo "   ✅ Config file already exists"
fi

echo "   ✅ English model complete!"

# Arabic model: ar_JO-kareem-medium
echo ""
echo "📥 Downloading Arabic model (ar_JO-kareem-medium)..."

if [ ! -f "ar_JO-kareem-medium/ar-jo-kareem-medium.onnx" ] || [ $(stat -f%z "ar_JO-kareem-medium/ar-jo-kareem-medium.onnx" 2>/dev/null || echo 0) -lt 1000 ]; then
    echo "   Downloading model file (this may take a few minutes)..."
    curl -L "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ar/ar_JO/kareem/medium/ar_JO-kareem-medium.onnx" \
         -o "ar_JO-kareem-medium/ar-jo-kareem-medium.onnx" \
         --progress-bar
    echo "   ✅ Model file downloaded"
else
    echo "   ✅ Model file already exists"
fi

if [ ! -f "ar_JO-kareem-medium/ar-jo-kareem-medium.onnx.json" ] || [ $(stat -f%z "ar_JO-kareem-medium/ar-jo-kareem-medium.onnx.json" 2>/dev/null || echo 0) -lt 100 ]; then
    echo "   Downloading config file..."
    curl -L "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ar/ar_JO/kareem/medium/ar_JO-kareem-medium.onnx.json" \
         -o "ar_JO-kareem-medium/ar-jo-kareem-medium.onnx.json"
    echo "   ✅ Config file downloaded"
else
    echo "   ✅ Config file already exists"
fi

echo "   ✅ Arabic model complete!"

cd ../..

echo ""
echo "===================================================="
echo "✅ All Piper TTS models downloaded successfully!"
echo ""
echo "📁 Model locations:"
echo "   English: models/piper/en_US-lessac-medium/"
echo "   Arabic:  models/piper/ar_JO-kareem-medium/"
echo ""
echo "📊 File sizes:"
echo ""
echo "English model:"
ls -lh models/piper/en_US-lessac-medium/
echo ""
echo "Arabic model:"
ls -lh models/piper/ar_JO-kareem-medium/
echo ""
echo "🎉 Ready to use Text-to-Speech!"
