// static/main.js  (Updated to show category)
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("uploadForm");
  const status = document.getElementById("status");
  const resultsArea = document.getElementById("resultsArea");
  const resultsDiv = document.getElementById("results");
  const queryImg = document.getElementById("queryImg");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    status.style.display = "inline";
    status.textContent = "Searching...";
    resultsArea.style.display = "none";
    resultsDiv.innerHTML = "";

    const formData = new FormData(form);

    try {
      const resp = await axios.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (resp.data.error) {
        alert("Error: " + resp.data.error);
        status.style.display = "none";
        return;
      }

      queryImg.src = resp.data.query_image;
      resultsArea.style.display = "block";
      const results = resp.data.results;

      results.forEach((r) => {
        const col = document.createElement("div");
        col.className = "col-12 col-md-6 col-lg-4";

        const card = document.createElement("div");
        card.className = "card h-100 shadow-sm";

        const img = document.createElement("img");
        img.className = "card-img-top";
        img.alt = r.name;
        img.src = r.image_url;

        const body = document.createElement("div");
        body.className = "card-body";

        const h5 = document.createElement("h5");
        h5.className = "card-title";
        h5.innerText = r.name;

        const cat = document.createElement("p");
        cat.className = "text-muted mb-1";
        cat.innerText = "Category: " + r.category;

        const p = document.createElement("p");
        p.className = "card-text";
        p.innerText = "Similarity: " + r.score.toFixed(4);

        body.appendChild(h5);
        body.appendChild(cat);
        body.appendChild(p);

        card.appendChild(img);
        card.appendChild(body);
        col.appendChild(card);
        resultsDiv.appendChild(col);
      });

      status.style.display = "none";
    } catch (err) {
      console.error(err);
      alert("Request failed: " + (err.response?.data?.error || err.message));
      status.style.display = "none";
    }
  });
});
