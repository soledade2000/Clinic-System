self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open("mc-cache-v1").then((cache) => {
      return cache.addAll([
        "/",
        "/index.html",
        "/dashboard.html",
        "/login.html",
        "/css/style.css",
        "/js/api.js",
        "/js/common.js"
      ]);
    })
  );
});

self.addEventListener("fetch", (e) => {
  e.respondWith(caches.match(e.request).then((r) => r || fetch(e.request)));
});
