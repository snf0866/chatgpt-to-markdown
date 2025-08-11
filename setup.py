from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chatgpt-to-markdown",
    version="1.0.0",
    author="snufkin0866",
    author_email="",
    description="Export ChatGPT conversations as beautiful markdown files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/snufkin0866/chatgpt-to-markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.40.0",
        "openai>=1.0.0",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "chatgpt-to-markdown=chatgpt_to_markdown:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/snufkin0866/chatgpt-to-markdown/issues",
        "Source": "https://github.com/snufkin0866/chatgpt-to-markdown",
    },
)