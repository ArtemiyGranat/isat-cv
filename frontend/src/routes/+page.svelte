<!-- src/routes/+page.svelte -->
<script context="module">
    export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
</script>

<script>
  let isLoadingScrape = false;
  let startPage = '';
  let amount = '';

  let isLoadingColor = false;
  let colorSearchResponse = [];
  let colorModel = -1;

  let isLoadingBlend = false;
  let blendResponse = [];

  let isLoadingImage = false;
  let imageSearchResponse = [];

  let isLoadingText = false;
  let textSearchQuery = '';
  let textSearchResponse = [];

  const scrape = async () => {
    if (!startPage || !amount) {
      alert('Please fill in all fields.');
      return;
    }
    
    isLoadingScrape = true;
    try {
      const url = `${BACKEND_URL}/scrape/${startPage}/${amount}`;
      const response = await fetch(url, { method: 'POST' });
    } catch (error) {
      console.error('Error:', error);
    } finally {
      isLoadingScrape = false;
    }
  };


  const colorSearch = async () => {
    isLoadingColor = true;
    try {
      const colorSearchFile = document.getElementById("colorSearchFile");
      if (colorSearchFile.files.length === 0 || colorModel == -1) {
        alert('Please upload a file and select a color model');
        return;
      }
      const colorModelTxt = (colorModel == 0) ? "lab" : "hsv";

      const formData = new FormData();
      formData.append('image', colorSearchFile.files[0]);

      const url = `${BACKEND_URL}/color_search/${colorModelTxt}`;
      const response = await fetch(url, { method: 'POST', body: formData });
      colorSearchResponse = await response.json();
    } catch (error) {
      console.error('Error:', error);
    } finally {
      isLoadingColor = false;
    }
  };

  const blend = async () => {
    isLoadingBlend = true;
    try {
      const blendImage1 = document.getElementById("blendImage1");
      const blendImage2 = document.getElementById("blendImage2");
      if (blendImage1.files.length === 0 || blendImage2.files.length == 0) {
        alert('Please upload two images');
        return;
      }

      const formData = new FormData();
      formData.append('first_image', blendImage1.files[0]);
      formData.append('second_image', blendImage2.files[0]);

      const url = `${BACKEND_URL}/blend/`;
      const response = await fetch(url, { method: 'POST', body: formData });
      const blob = await response.blob();
      blendResponse = [URL.createObjectURL(blob)]
    } catch (error) {
      console.error('Error:', error);
    } finally {
      isLoadingBlend = false;
    }
  };

  const imageSearch = async () => {
    isLoadingImage = true;
    try {
      const colorSearchFile = document.getElementById("imageSearchFile");
      if (imageSearchFile.files.length === 0) {
        alert('Please upload a file');
        return;
      }

      const formData = new FormData();
      formData.append('image', colorSearchFile.files[0]);

      const url = `${BACKEND_URL}/image_search/`;
      const response = await fetch(url, { method: 'POST', body: formData });
      imageSearchResponse = await response.json();
    } catch (error) {
      console.error('Error:', error);
    } finally {
      isLoadingImage= false;
    }
  };

  const textSearch = async () => {
    isLoadingText = true;
    try {
      const url = `${BACKEND_URL}/text_search/?query=${textSearchQuery}`;
      const response = await fetch(url, { method: 'POST' });
      textSearchResponse = await response.json();
    } catch (error) {
      console.error('Error:', error);
    } finally {
      isLoadingText = false;
    }
  };
</script>

<main>
  <h1>Educational Project</h1>

  <h1>Scraper</h1>
  <h3>Fill in start page and amount of images to be scraped, then click on "Scrape" button</h3>
  <div class="input-group">
    <input type="text" id="startPage" bind:value={startPage} placeholder="Enter start page" />
    <input type="number" id="amount" bind:value={amount} placeholder="Enter amount" />
  </div>
  <button on:click={scrape} disabled={isLoadingScrape}>
    {isLoadingScrape ? 'Loading...' : 'Scrape'}
  </button>

  <h1>Color search</h1>
  <h3>Upload image and select color model (LAB or HSV), then click on "Search" button</h3>
  <div class="input-group">
     <input type="file" id="colorSearchFile" accept="image/*" />
     <label>
     <input type="radio" bind:group={colorModel} value={0} /> LAB
     </label>
     <label>
     <input type="radio" bind:group={colorModel} value={1} /> HSV
     </label>
  </div>
  <button on:click={colorSearch} disabled={isLoadingColor}>
    {isLoadingColor ? 'Loading...' : 'Search for 10 images with most complementary median color'}
  </button>
  <div class="image-grid">
    {#each colorSearchResponse as imageUrl}
        <img src={imageUrl} alt="Image" />
    {/each}
  </div>
    
  <h1>Image blending using Laplacian and Gaussian pyramids</h1>
  <h3>Upload two images, then click on "Blend" button</h3>
  <div class="input-group">
     <input type="file" id="blendImage1" accept="image/*" />
     <input type="file" id="blendImage2" accept="image/*" />
  </div>
  <button on:click={blend} disabled={isLoadingBlend}>
    {isLoadingBlend ? 'Loading...' : 'Blend images'}
  </button>
  <div class="blended-image">
    {#each blendResponse as imageUrl}
        <img src={imageUrl} alt="Blended image" />
    {/each}
  </div>

  <h1>Image search</h1>
  <h3>Upload image, then click on "Search" button</h3>
  <div class="input-group">
     <input type="file" id="imageSearchFile" accept="image/*" />
  </div>
  <button on:click={imageSearch} disabled={isLoadingImage}>
    {isLoadingColor ? 'Loading...' : 'Search for 10 similar images'}
  </button>
  <div class="image-grid">
    {#each imageSearchResponse as imageUrl}
        <img src={imageUrl} alt="Image" />
    {/each}
  </div>

  <h1>Text search</h1>
  <h3>Enter query, then click on "Search" button</h3>
  <div class="input-group">
    <input type="text" id="textSearchQuery" bind:value={textSearchQuery} placeholder="Enter query" />
  </div>
  <button on:click={textSearch} disabled={isLoadingText}>
    {isLoadingText ? 'Loading...' : 'Find 10 images that match your request'}
  </button>
  <div class="image-grid">
    {#each textSearchResponse as imageUrl}
        <img src={imageUrl} alt="Image" />
    {/each}
  </div>
</main>

<style>
  @font-face {
    font-family: 'Inter-Regular';
    src: url('Inter-Regular.woff2') format('woff2'),
      url('Inter-Regular.woff') format('woff');
    font-display: swap;
    font-style: normal;
  }

  * {
    font-family: -apple-system, 'Inter-Regular';
  }

  main {
    text-align: center;
    padding: 1.5em;
    max-width: 65%;
    margin: 0 auto;
  }

  h1 {
    color: #3498db;
    font-size: 2em;
    font-weight: normal;
    margin-bottom: 15px;
  }

  h2 {
    font-weight: normal;
  }

  .input-group {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
    text-align: left;
  }

  .input-group input {
    padding: 8px;
    margin-bottom: 8px;
    box-sizing: border-box;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 0.9em;
  }

  button {
    font-family: 'Inter-Regular';
    background-color: #3498db;
    color: white;
    padding: 10px 20px;
    font-size: 1em;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }

  button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }

  button:hover:enabled {
    background-color: #217dbb;
  }

  .image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); /* Adjust the minmax values as needed */
    gap: 10px;
    padding: 10px;
  }

  .image-grid img {
    width: 100%;
    height: auto;
    object-fit: cover;
  }

  .blended-image {
    padding: 10px;
  }

  .blended-image img {
    width: 30%;
    height: auto;
    object-fit: cover;
  }

</style>
