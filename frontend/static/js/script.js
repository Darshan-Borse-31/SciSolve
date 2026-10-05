/* SciSolve frontend.
 *
 * Views are switched with the URL hash so the browser Back button works:
 *   (empty)      landing page
 *   #home        application, no module selected
 *   #m/<id>      application, chat for one module
 *   #how, #about information pages
 *
 * Conversations live only in memory. Reloading the page clears them.
 */
(() => {
  'use strict';

  const MODULES = JSON.parse(document.getElementById('modules-data').textContent);
  const byId = Object.fromEntries(MODULES.map((m) => [m.id, m]));

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const mobileQuery = window.matchMedia('(max-width: 860px)');

  const landing = $('#landing');
  const app = $('#app');
  const views = {
    home: $('#view-home'),
    chat: $('#view-chat'),
    how: $('#view-how'),
    about: $('#view-about'),
  };
  const menuBtn = $('#menu-btn');
  const backdrop = $('#backdrop');
  const newChatBtn = $('#new-chat');
  const navLinks = $$('[data-nav]');
  const statusEl = $('#status');
  const chatTitle = $('#chat-title');
  const chatDesc = $('#chat-desc');
  const chatSymbol = $('#chat-symbol');
  const scrollEl = $('#chat-scroll');
  const messagesEl = $('#messages');
  const inputEl = $('#input');
  const sendBtn = $('#send');

  const state = {
    module: null,          // last module the user opened
    conversations: {},     // module id -> array of messages
    pendingModule: null,   // module id with a request in flight
    ticket: 0,             // identifies the latest request
  };

  /* ---------- Small helpers ---------- */

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function conversation(id) {
    if (!state.conversations[id]) state.conversations[id] = [];
    return state.conversations[id];
  }

  /* ---------- Sidebar ---------- */

  function sidebarIsOpen() {
    return mobileQuery.matches
      ? app.classList.contains('sidebar-open')
      : !app.classList.contains('sidebar-collapsed');
  }

  function setSidebar(open) {
    if (mobileQuery.matches) app.classList.toggle('sidebar-open', open);
    else app.classList.toggle('sidebar-collapsed', !open);
    menuBtn.setAttribute('aria-expanded', String(open));
  }

  function closeMobileSidebar() {
    if (mobileQuery.matches) setSidebar(false);
  }

  menuBtn.addEventListener('click', () => setSidebar(!sidebarIsOpen()));
  backdrop.addEventListener('click', closeMobileSidebar);
  navLinks.forEach((link) => link.addEventListener('click', closeMobileSidebar));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMobileSidebar();
  });
  mobileQuery.addEventListener('change', () => {
    app.classList.remove('sidebar-open');
    menuBtn.setAttribute('aria-expanded', String(sidebarIsOpen()));
  });
  menuBtn.setAttribute('aria-expanded', String(sidebarIsOpen()));

  /* ---------- Routing ---------- */

  function showLanding() {
    landing.hidden = false;
    app.hidden = true;
    document.title = 'SciSolve — Scientific Computing Assistant';
    window.scrollTo(0, 0);
  }

  function showApp() {
    landing.hidden = true;
    app.hidden = false;
  }

  function setView(name, activeKey, title) {
    Object.entries(views).forEach(([key, node]) => { node.hidden = key !== name; });
    navLinks.forEach((link) => {
      if (link.dataset.nav === activeKey) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    document.title = title ? `SciSolve — ${title}` : 'SciSolve';
    views[name].scrollTop = 0;
  }

  function openModule(id) {
    const mod = byId[id];
    state.module = id;
    setView('chat', `m/${id}`, mod.name);
    chatTitle.textContent = mod.title;
    chatDesc.textContent = mod.description;
    chatSymbol.textContent = mod.symbol;
    inputEl.placeholder = mod.placeholder;
    renderChat();
    if (!mobileQuery.matches) inputEl.focus();
  }

  function route() {
    const hash = location.hash.replace(/^#\/?/, '');
    if (!hash) { showLanding(); return; }
    showApp();
    if (hash.startsWith('m/') && byId[hash.slice(2)]) openModule(hash.slice(2));
    else if (hash === 'how') setView('how', 'how', 'How It Works');
    else if (hash === 'about') setView('about', 'about', 'About');
    else setView('home', null, 'Home');
  }

  window.addEventListener('hashchange', route);

  /* ---------- New chat ---------- */

  newChatBtn.addEventListener('click', () => {
    closeMobileSidebar();
    const id = state.module;
    if (!id) {
      location.hash = '#home';
      return;
    }
    state.conversations[id] = [];
    if (state.pendingModule === id) state.pendingModule = null; // ignore the old reply
    if (location.hash === `#m/${id}`) openModule(id);
    else location.hash = `#m/${id}`;
  });

  /* ---------- Rendering messages ---------- */

  function renderEmpty(mod) {
    const box = el('div', 'empty');
    box.appendChild(el('h2', null, 'Try an example'));
    box.appendChild(el('p', null, 'Choose one to fill the box, then edit it or press Send.'));
    const chips = el('div', 'chips');
    mod.examples.forEach((text) => {
      const chip = el('button', 'chip', text);
      chip.type = 'button';
      chip.addEventListener('click', () => {
        inputEl.value = text;
        autosize();
        inputEl.focus();
      });
      chips.appendChild(chip);
    });
    box.appendChild(chips);
    return box;
  }

  function renderUser(text) {
    const row = el('div', 'msg msg-user');
    row.appendChild(el('div', 'bubble', text));
    return row;
  }

  function renderResultBody(result) {
    const card = el('div', 'result');

    if (result.normalized && result.input && result.normalized !== result.input) {
      const note = el('p', 'result-note', 'Read as: ');
      note.appendChild(el('code', null, result.normalized));
      card.appendChild(note);
    }

    if (result.status === 'ok') {
      if (result.title) card.appendChild(el('h3', null, result.title));

      if (Array.isArray(result.steps) && result.steps.length) {
        const list = el('ol', 'steps');
        result.steps.forEach((step) => {
          const item = el('li');
          item.appendChild(el('div', 'step-title', step.title));
          if (step.detail) item.appendChild(el('div', 'step-detail', step.detail));
          list.appendChild(item);
        });
        card.appendChild(list);
      }

      if (result.answer) {
        const answer = el('div', 'answer');
        answer.appendChild(el('span', 'answer-label', 'Answer'));
        answer.appendChild(document.createTextNode(result.answer));
        card.appendChild(answer);
      }

      if (typeof result.image === 'string' && /^[A-Za-z0-9+/=]+$/.test(result.image)) {
        const img = el('img', 'result-image');
        img.src = `data:image/png;base64,${result.image}`;
        img.alt = 'Generated graph';
        card.appendChild(img);
      }
    } else if (result.status === 'not_implemented') {
      const notice = el('div', 'notice');
      notice.appendChild(el('strong', null, 'Not built yet'));
      notice.appendChild(document.createTextNode(result.message || 'This module is not implemented yet.'));
      card.appendChild(notice);
    } else {
      const notice = el('div', 'notice is-error');
      notice.appendChild(el('strong', null, 'Could not solve this'));
      notice.appendChild(document.createTextNode(result.message || 'Something went wrong.'));
      card.appendChild(notice);
    }
    return card;
  }

  function renderBot(mod, bodyNode) {
    const row = el('div', 'msg msg-bot');
    row.appendChild(el('span', 'avatar', mod.symbol));
    row.appendChild(bodyNode);
    return row;
  }

  function renderChat() {
    const id = state.module;
    if (!id) return;
    const mod = byId[id];
    const convo = conversation(id);
    const pending = state.pendingModule === id;

    messagesEl.replaceChildren();
    if (!convo.length && !pending) messagesEl.appendChild(renderEmpty(mod));

    convo.forEach((message) => {
      if (message.role === 'user') messagesEl.appendChild(renderUser(message.text));
      else messagesEl.appendChild(renderBot(mod, renderResultBody(message.result)));
    });

    if (pending) {
      const wait = el('div', 'result pending', 'Working on it…');
      messagesEl.appendChild(renderBot(mod, wait));
    }

    sendBtn.disabled = pending;
    scrollEl.scrollTop = scrollEl.scrollHeight;
  }

  /* ---------- Sending ---------- */

  function autosize() {
    inputEl.style.height = 'auto';
    inputEl.style.height = `${Math.min(inputEl.scrollHeight, 160)}px`;
  }

  async function send() {
    const id = state.module;
    const text = inputEl.value.trim();
    if (!id || !text || state.pendingModule === id) return;

    const convo = conversation(id);
    convo.push({ role: 'user', text });
    inputEl.value = '';
    autosize();

    const ticket = ++state.ticket;
    state.pendingModule = id;
    renderChat();

    let result;
    try {
      const response = await fetch('/api/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ module: id, query: text }),
      });
      try {
        result = await response.json();
      } catch (_parseError) {
        result = { status: 'error', message: `The server replied with status ${response.status}.` };
      }
    } catch (_networkError) {
      result = { status: 'error', message: 'Could not reach the SciSolve server. Check that it is still running.' };
      setStatus(false);
    }

    // Ignore the reply if the user started a new chat while it was in flight.
    if (state.conversations[id] === convo) convo.push({ role: 'assistant', result });
    if (state.ticket === ticket && state.pendingModule === id) state.pendingModule = null;
    if (state.module === id) renderChat();
  }

  sendBtn.addEventListener('click', send);
  inputEl.addEventListener('input', autosize);
  inputEl.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      send();
    }
  });

  /* ---------- Server status indicator ---------- */

  function setStatus(online) {
    statusEl.dataset.state = online ? 'online' : 'offline';
    $('.status-text', statusEl).textContent = online ? 'Server online' : 'Server offline';
  }

  async function checkHealth() {
    try {
      const response = await fetch('/api/health', { cache: 'no-store' });
      setStatus(response.ok);
    } catch (_error) {
      setStatus(false);
    }
  }

  /* ---------- Start ---------- */

  route();
  checkHealth();
  setInterval(checkHealth, 30000);
})();
