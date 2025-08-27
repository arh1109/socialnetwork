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


// dynamic multi-pick: each click creates its own hidden file input named "attachments"
(function () {
  const form = document.getElementById("composer-form");
  const host = document.getElementById("file-inputs");
  const gridWrap = document.getElementById("thumb-grid-wrap");
  const grid = document.getElementById("thumb-grid");
  const toggleBtn = document.getElementById("thumbs-toggle");
  const btnPhoto = document.getElementById("add-photo");
  const btnVideo = document.getElementById("add-video");
  if (!form || !host || !grid || !btnPhoto || !btnVideo) return;

  function addThumb(file) {
    const url = URL.createObjectURL(file);
    const cell = document.createElement("div");
    cell.className = "thumb";
    if (file.type.startsWith("image/")) {
      const img = document.createElement("img");
      img.src = url;
      cell.appendChild(img);
    } else if (file.type.startsWith("video/")) {
      const v = document.createElement("video");
      v.src = url; v.muted = true;
      cell.appendChild(v);
    } else {
      cell.textContent = "file";
    }
    grid.appendChild(cell);
    gridWrap.hidden = false;
    toggleBtn.hidden = grid.children.length <= 12;
  }

  function makePicker(accept) {
    const input = document.createElement("input");
    input.type = "file";
    input.name = "attachments";     // crucial: same name for all inputs
    input.multiple = true;          // allow many per pick if user wants
    input.accept = accept;
    input.className = "visually-hidden-file";
    host.appendChild(input);

    input.addEventListener("change", () => {
      const files = Array.from(input.files || []);
      if (files.length === 0) { input.remove(); return; }
      files.forEach(addThumb);
      // keep the input in the DOM so these files submit with the form
    }, { once: true });

    input.click();
  }

  btnPhoto.addEventListener("click", () => makePicker("image/*,.jpg,.jpeg,.png,.gif,.webp"));
  btnVideo.addEventListener("click", () => makePicker("video/*,.mp4,.webm,.ogv"));
  
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

// Post 3-dot menu: toggle + click-outside + Esc
(function () {
  const buttons = document.querySelectorAll(".post-menu .menu-btn");
  if (!buttons.length) return;

  const closeAll = () => {
    document.querySelectorAll(".post-menu .menu").forEach(menu => {
      menu.hidden = true;
      const btn = menu.parentElement.querySelector(".menu-btn");
      if (btn) btn.setAttribute("aria-expanded", "false");
    });
  };

  // Toggle the menu for each post
  buttons.forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation(); // don't trigger document click
      const id = btn.getAttribute("aria-controls");
      const menu = document.getElementById(id);
      if (!menu) return;
      const willOpen = menu.hidden;
      closeAll();
      if (willOpen) {
        menu.hidden = false;
        btn.setAttribute("aria-expanded", "true");
      }
    });
  });

  // CSRF helper
  function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : "";
  }
  const csrftoken = getCookie("csrftoken");

  // Delete handler
  document.querySelectorAll(".post-menu .post-delete").forEach(link => {
    link.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();

      const postId = link.dataset.postId;
      const postCard = link.closest(".post");
      if (!postCard) return;

      // Close the dropdown
      const menu = link.closest(".menu");
      if (menu) {
        menu.hidden = true;
        const btn = postCard.querySelector(".menu-btn");
        btn && btn.setAttribute("aria-expanded", "false");
      }

      if (!confirm("Delete this post? This will remove its images from the server.")) return;

      try {
        const resp = await fetch(`/post/${postId}/delete/`, {
          method: "POST",
          headers: { "X-CSRFToken": csrftoken },
        });
        const data = await resp.json().catch(() => ({}));
        if (!resp.ok || !data.ok) throw new Error(data.error || "Delete failed");

        // Remove from DOM (optional fade-out)
        postCard.style.transition = "opacity 200ms ease";
        postCard.style.opacity = "0";
        setTimeout(() => postCard.remove(), 220);
      } catch (err) {
        alert(err.message || "Could not delete post.");
      }
    });
  });

  // Nice-to-have: prevent clicks inside the dropdown from closing it immediately
  document.querySelectorAll(".post-menu .menu").forEach(menu => {
    menu.addEventListener("click", (e) => e.stopPropagation());
  });

  // Optional: clicking "Close" link just closes the menu
  document.querySelectorAll(".post-menu .menu a").forEach(a => {
    if (a.textContent.trim().toLowerCase() === "close") {
      a.addEventListener("click", (e) => { e.preventDefault(); closeAll(); });
    }
  });

  // Click anywhere else closes any open menu
  document.addEventListener("click", closeAll);

  // Escape key closes
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeAll();
  });
})();

// Inline edit for post text
(function () {
  // Helper: get CSRF token (Django docs)
  function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : "";
  }
  const csrftoken = getCookie("csrftoken");

  // Click handler for "Edit"
  document.querySelectorAll(".post-menu .post-edit").forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();

      const postId = link.dataset.postId;
      const postCard = link.closest(".post");
      if (!postCard) return;

      // Close the dropdown
      const menu = link.closest(".menu");
      if (menu) {
        menu.hidden = true;
        const btn = postCard.querySelector(".menu-btn");
        btn && btn.setAttribute("aria-expanded", "false");
      }

      // Target area for text / editor
      const wrap = postCard.querySelector(`.post-text-wrap[data-post-id="${postId}"]`);
      if (!wrap) return;

      // If already in edit mode, do nothing
      if (wrap.querySelector("textarea")) return;

      // Grab existing text (preserve \n)
      const existingDisplay = wrap.querySelector(".post-text");
      const existingText = existingDisplay ? existingDisplay.textContent : "";

      // Build textarea + save button
      const ta = document.createElement("textarea");
      ta.className = "composer-textarea";
      ta.rows = Math.min(6, Math.max(2, (existingText.split("\n").length)));
      ta.value = existingText;

      const saveBtn = document.createElement("button");
      saveBtn.type = "button";
      saveBtn.className = "btn-primary";
      saveBtn.textContent = "Save";
      saveBtn.style.marginTop = "8px";

      // Replace display with editor
      wrap.innerHTML = "";
      wrap.appendChild(ta);
      wrap.appendChild(saveBtn);
      ta.focus();

      // Save handler
      saveBtn.addEventListener("click", async () => {
        saveBtn.disabled = true;

        try {
          const formData = new FormData();
          formData.append("text", ta.value);

          const resp = await fetch(`/post/${postId}/edit/`, {
            method: "POST",
            headers: { "X-CSRFToken": csrftoken },
            body: formData,
          });
          const data = await resp.json();
          if (!resp.ok || !data.ok) throw new Error(data.error || "Save failed");

          // Render back as clamped HTML (convert \n -> <br>)
          const html = (data.text || "").replace(/\n/g, "<br>");

          // Rebuild the display text + (re)create "Read more" button
          wrap.innerHTML = "";
          const display = document.createElement("div");
          display.className = "post-text clamp-5";
          display.setAttribute("data-post-id", postId);
          display.innerHTML = html;
          wrap.appendChild(display);

          // Ensure the Read more button exists/behaves
          let rm = postCard.querySelector(`.read-more[data-target="${postId}"]`);
          if (!rm) {
            rm = document.createElement("button");
            rm.type = "button";
            rm.className = "linklike read-more";
            rm.setAttribute("data-target", postId);
            rm.hidden = true;
            wrap.appendChild(rm);
          }
          // Re-evaluate clamp to show/hide the button
          requestAnimationFrame(() => {
            if (display.scrollHeight > display.clientHeight + 2) {
              rm.hidden = false;
              rm.textContent = "Read more";
              rm.onclick = () => {
                display.classList.toggle("expanded");
                rm.textContent = display.classList.contains("expanded") ? "Show less" : "Read more";
              };
            } else {
              rm.hidden = true;
            }
          });

          // Show/persist the "Edited" badge
          let badge = postCard.querySelector(".edited-badge");
          if (!badge) {
            badge = document.createElement("span");
            badge.className = "edited-badge";
            badge.textContent = "Edited";
            const usernameEl = postCard.querySelector(".username");
            usernameEl && usernameEl.appendChild(badge);
          }

        } catch (err) {
          alert(err.message || "Failed to save");
        } finally {
          saveBtn.disabled = false;
        }
      });
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

