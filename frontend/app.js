const { useState, useCallback } = React;

function App() {
    const [file, setFile] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setError(null);
            setResult(null);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError("Please select an audio file");
            return;
        }

        setIsProcessing(true);
        setError(null);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("http://localhost:8000/transcribe", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Error processing audio");
            }

            setResult(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="max-w-3xl mx-auto">
                <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
                    Voice Scribe
                </h1>

                <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                            <input
                                type="file"
                                accept="audio/*"
                                onChange={handleFileChange}
                                className="hidden"
                                id="audio-file"
                            />
                            <label
                                htmlFor="audio-file"
                                className="cursor-pointer text-blue-500 hover:text-blue-600"
                            >
                                {file ? file.name : "Click to select audio file"}
                            </label>
                        </div>

                        <button
                            type="submit"
                            disabled={isProcessing || !file}
                            className={`w-full py-2 px-4 rounded-lg text-white font-semibold ${
                                isProcessing || !file
                                    ? "bg-gray-400 cursor-not-allowed"
                                    : "bg-blue-500 hover:bg-blue-600"
                            }`}
                        >
                            {isProcessing ? "Processing..." : "Transcribe"}
                        </button>
                    </form>
                </div>

                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                        {error}
                    </div>
                )}

                {result && (
                    <div className="space-y-6">
                        <div className="bg-white rounded-lg shadow-lg p-6">
                            <h2 className="text-xl font-semibold mb-4 text-gray-800">
                                Raw Transcription
                            </h2>
                            <p className="text-gray-600 whitespace-pre-wrap">
                                {result.raw_transcription}
                            </p>
                        </div>

                        <div className="bg-white rounded-lg shadow-lg p-6">
                            <h2 className="text-xl font-semibold mb-4 text-gray-800">
                                Sanitized Text
                            </h2>
                            <p className="text-gray-600 whitespace-pre-wrap">
                                {result.sanitized_text}
                            </p>
                        </div>

                        <div className="text-sm text-gray-500 text-right">
                            Processing time: {result.processing_time.toFixed(2)} seconds
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById("root")); 