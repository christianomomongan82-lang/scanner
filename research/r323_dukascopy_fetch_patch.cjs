// Add browser-like headers required by the Dukascopy JETTA data API.
// This file is loaded via NODE_OPTIONS only for the downloader child process.
const nativeFetch = globalThis.fetch;

globalThis.fetch = function patchedFetch(input, init = {}) {
  let requestUrl;
  try {
    requestUrl = input instanceof Request ? input.url : String(input);
    if (new URL(requestUrl).hostname !== "jetta.dukascopy.com") {
      return nativeFetch.call(globalThis, input, init);
    }
  } catch {
    return nativeFetch.call(globalThis, input, init);
  }

  const inheritedHeaders = input instanceof Request ? input.headers : undefined;
  const headers = new Headers(init.headers || inheritedHeaders || undefined);
  headers.set(
    "User-Agent",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
  );
  headers.set("Accept", "application/json, text/plain, */*");
  headers.set("Origin", "https://www.dukascopy.com");
  headers.set("Referer", "https://www.dukascopy.com/");

  return nativeFetch.call(globalThis, input, { ...init, headers });
};
