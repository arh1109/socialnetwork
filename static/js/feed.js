// static/js/feed.js

// Auto-resize composer textarea up to max-height
(function () {
  const ta = document.querySelector(".composer-textarea");
  if (!ta) return;
  const maxH = parseInt(getComputedStyle(ta).maxHeight, 10) || 160;
  const resize = () => {
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, maxH) + "px";
  };
  ta.addEventListener("input", resize);
  resize();
})();

// Attachment previews + Show more (composer)
(function () {
  const input = document.querySelector("#composer-form input[type=file]");
  const gridWrap = document.getElementById("thumb-grid-wrap");
  const grid = document.getElementById("thumb-grid");
  const toggleBtn = document.getElementById("thumbs-toggle");
  if (!input || !grid || !gridWrap) return;

  const renderThumb = (file, url) => {
    const cell = document.createElement("div");
    cell.className = "thumb";
    if (file.type.startsWith("image/")) {
      const img = document.createElement("img");
      img.src = url;
      cell.appendChild(img);
    } else if (file.type.startsWith("video/")) {
      const v = document.createElement("video");
      v.src = url;
      v.muted = true;
      cell.appendChild(v);
    } else {
      cell.textContent = "file";
    }
    grid.appendChild(cell);
  };

  input.addEventListener("change", () => {
    grid.innerHTML = "";
    const files = Array.from(input.files || []);
    if (!files.length) {
      gridWrap.hidden = true;
      toggleBtn.hidden = true;
      return;
    }
    files.forEach(f => {
      const url = URL.createObjectURL(f);
      renderThumb(f, url);
    });
    gridWrap.hidden = false;
    // show toggle only if more than 2 rows worth (~12 thumbs since 6 per row)
    toggleBtn.hidden = files.length <= 12;
  });

  toggleBtn?.addEventListener("click", () => {
    const expanded = grid.classList.toggle("expanded");
    toggleBtn.textContent = expanded ? "Show less" : "Show more";
  });
})();

// Post "Read more" (removes 5-line clamp)
(function () {
  document.querySelectorAll(".post-text.clamp-5").forEach(el => {
    const id = el.dataset.postId;
    const btn = document.querySelector(`.read-more[data-target="${id}"]`);
    if (!btn) return;
    // Only show the button if it's actually clamped (rough heuristic)
    if (el.scrollHeight <= el.clientHeight + 2) return; // not overflowing
    btn.hidden = false;
    btn.addEventListener("click", () => {
      el.classList.toggle("expanded");
      btn.textContent = el.classList.contains("expanded") ? "Show less" : "Read more";
    });
  });
})();

// Post "View more" for media grid (>2 rows)
(function () {
  document.querySelectorAll(".view-more").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.target;
      const wrap = document.querySelector(`.media-grid-wrap[data-post-id="${id}"]`);
      if (!wrap) return;
      const exp = wrap.classList.toggle("expanded");
      btn.textContent = exp ? "View less" : "View more";
    });
  });
})();

// Toggle comments
(function () {
  document.querySelectorAll(".comment-toggle").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.target;
      const box = document.getElementById(`comments-${id}`);
      if (!box) return;
      box.hidden = !box.hidden;
      if (!box.hidden) {
        const ta = box.querySelector("textarea");
        ta && ta.focus();
      }
    });
  });
})();

// static/js/feed.js
(function () {
  const box = document.getElementById("feed-flash");
  if (!box) return;
  const ms = parseInt(box.dataset.autodismiss || "5000", 10);
  setTimeout(() => {
    box.classList.add("fade-out");
    setTimeout(() => box.remove(), 320);
  }, ms);
})();

