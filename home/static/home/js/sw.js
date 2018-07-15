var CACHE_NAME = 'xanana-cache-v1';

var urlsToCache = [
  '/',
  '/static/home/css/bootstrap.min.css',
  '/static/home/fonts/font-awesome/css/font-awesome.min.css',
  '/static/home/js/bootstrap.min.js',
  '/static/home/css/xanana.css'
];


self.addEventListener('install', function(event) {
  // Perform install steps
  var cachingCompleted = caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      }).then(() => self.skipWaiting());

      event.waitUntil(cachingCompleted);  
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Cache hit - return response
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});


self.addEventListener('activate', function(event) {
  console.log('Activated', event);
});
self.addEventListener('push', function(event) {
  console.log('Push message received', event);
  // TODO
});