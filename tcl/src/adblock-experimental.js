/* Experimental local patch for the supplied YouTube TV 7.27.302 APK.
 * No remote scripts, telemetry, or network endpoints are added.
 */
(function () {
  'use strict';
  if (location.hostname !== 'www.youtube.com' && location.hostname !== 'youtube.com') return;
  if (window.__localTvAdPatch) return;
  window.__localTvAdPatch = { version: 1, removed: 0, skipped: 0 };
  var state = window.__localTvAdPatch;
  var fields = new Set(['adPlacements', 'playerAds', 'adSlots', 'adBreaks']);
  function clean(root) {
    if (!root || typeof root !== 'object') return root;
    var stack = [root], seen = new WeakSet(), remaining = 20000;
    while (stack.length && remaining-- > 0) {
      var item = stack.pop();
      if (!item || typeof item !== 'object' || seen.has(item)) continue;
      seen.add(item);
      Object.keys(item).forEach(function (key) {
        if (fields.has(key) && Array.isArray(item[key])) {
          if (item[key].length) { item[key] = []; state.removed++; }
        } else if (item[key] && typeof item[key] === 'object') stack.push(item[key]);
      });
    }
    return root;
  }
  var parse = JSON.parse;
  JSON.parse = function () { return clean(Reflect.apply(parse, this, arguments)); };
  if (typeof Response !== 'undefined' && Response.prototype.json) {
    var responseJson = Response.prototype.json;
    Response.prototype.json = function () {
      return Reflect.apply(responseJson, this, arguments).then(clean);
    };
  }
  clean(window.ytInitialPlayerResponse);
  clean(window.ytInitialData);
  var lastButton = null, lastClick = 0;
  function skipAvailableAd() {
    try {
      var buttons = document.querySelectorAll(
        '.ytp-ad-skip-button, .ytp-ad-skip-button-modern, ' +
        '.ytlr-ad-skip-button, .ytlr-skip-ad-button, .ytlr-ad-skip-button-renderer'
      );
      for (var i = 0; i < buttons.length; i++) {
        var button = buttons[i];
        if (button.getAttribute('aria-disabled') === 'true' || button.disabled) continue;
        var rect = button.getBoundingClientRect();
        var style = getComputedStyle(button);
        if (!rect.width || !rect.height || style.visibility === 'hidden' || style.display === 'none') continue;
        var now = Date.now();
        if (button === lastButton && now - lastClick < 1500) continue;
        button.click(); lastButton = button; lastClick = now; state.skipped++;
        break;
      }
    } catch (_) { /* A changed page layout must not stop playback. */ }
  }
  window.setInterval(skipAvailableAd, 750);
  console.info('[LocalTvAdPatch] experimental patch installed');
})();
