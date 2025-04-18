# PixAni

PixAni is a web to download anime cover images from AniList and store personalized data using steganography.

## Features

- **Anime Cover Downloads**: Fetch and download high-quality anime cover images directly from AniList.
- **Personalized Metadata**: Store custom data such as:
    - Personal ratings
    - Reviews
    - Notes
    - Download links
- **Steganography**: Embed metadata securely within the downloaded images without altering their visual quality.
- **Additional Metadata**: Support for storing other relevant information about the anime.

## How It Works

1. Search for your favorite anime using the AniList API.
2. Download the cover image of the anime.
3. Add personalized metadata, including ratings, reviews, and notes.
4. Save the image with embedded metadata using steganography.
5. Retrieve and view the stored metadata anytime.


## Getting Started

1. Clone the repository:
    ```bash
    git clone https://github.com/Rigelyon/PixAni.git
    ```
2. Navigate to the project directory:
    ```bash
    cd PixAni
    ```
3. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Apply database migrations:
    ```bash
    python manage.py migrate
    ```
6. Start the development server:
    ```bash
    python manage.py runserver
    ```
7. Access the application at `http://127.0.0.1:8000`.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve PixAni.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [AniList API](https://anilist.co/) for providing anime data.
- Open-source libraries and tools used in the project.

Enjoy managing your anime collection with PixAni!