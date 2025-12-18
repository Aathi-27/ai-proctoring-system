from setuptools import setup, find_packages

setup(
    name="audio-vad-pipeline",
    version="1.0.0",
    description="Real-time Voice Activity Detection and Audio Analysis Pipeline",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "flask==2.3.2",
        "flask-cors==4.0.0",
        "librosa==0.10.0",
        "numpy==1.24.3",
        "scipy==1.11.1",
        "silero-vad==5.0.0",
        "torch==2.0.1",
        "scikit-learn==1.3.0",
        "pymongo==4.4.1",
        "pytest==7.4.0",
        "pytest-cov==4.1.0",
        "pytest-mock==3.11.1",
        "python-dotenv==1.0.0",
        "pydantic==2.0.2",
    ],
)
