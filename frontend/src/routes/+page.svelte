<!-- src/routes/+page.svelte -->
<script context="module">
	export const BACKEND_URL = 'http://0.0.0.0:8000';
</script>

<script>
  let isLoadingScrape = false;
  let isLoadingColor = false;
  let startPage = '';
  let amount = '';

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
      if (colorSearchFile.files.length === 0) {
        alert('Please upload a file');
        return;
      }
      const formData = new FormData();
      formData.append('image', colorSearchFile.files[0]);

      const url = `${BACKEND_URL}/color_search/`;
      const response = await fetch(url, { method: 'POST', body: formData });
    } catch (error) {
      console.error('Error:', error);
    } finally {
      isLoadingColor = false;
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
  <h3>Upload image, then click on "Search" button</h3>
  <div class="input-group">
     <input type="file" id="colorSearchFile" accept="image/*" />
  </div>
  <button on:click={colorSearch} disabled={isLoadingColor}>
    {isLoadingColor ? 'Loading...' : 'Search for 10 images with most complementary median color'}
  </button>
    

</main>

<style>
  main {
    text-align: center;
    padding: 1.5em;
    max-width: 360px;
    margin: 0 auto;
  }

  h1 {
    color: #3498db;
    font-size: 2em;
    font-weight: 700;
    margin-bottom: 15px;
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
</style>
