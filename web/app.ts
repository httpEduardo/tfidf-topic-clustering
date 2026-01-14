const results = document.getElementById("results") as HTMLDivElement;
const clusterButton = document.getElementById("clusterButton") as HTMLButtonElement;
const seedButton = document.getElementById("seedButton") as HTMLButtonElement;

type ClusterDoc = { title: string };

type ClusterData = { terms: string[]; docs: ClusterDoc[] };

function renderClusters(clusters: Record<string, ClusterData>): void {
  results.innerHTML = "";
  Object.entries(clusters).forEach(([clusterId, data]) => {
    const section = document.createElement("section");
    section.className = "cluster";
    const terms = data.terms.join(", ");
    section.innerHTML = `<h3>Cluster ${clusterId}</h3><p>${terms}</p><ul>${data.docs
      .map((doc) => `<li>${doc.title}</li>`)
      .join("")}</ul>`;
    results.appendChild(section);
  });
}

clusterButton.addEventListener("click", () => {
  const k = parseInt((document.getElementById("kInput") as HTMLInputElement).value, 10);
  fetch("/api/cluster", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ k }),
  })
    .then((res) => res.json())
    .then((data) => renderClusters(data.clusters || {}));
});

seedButton.addEventListener("click", () => {
  fetch("/api/seed", { method: "POST" })
    .then((res) => res.json())
    .then(() => alert("Sample docs loaded."));
});
