"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const { shouldSendOnKeydown } = require("../dashboard/app.js");

test("Enter sends a chat message", () => {
  assert.equal(shouldSendOnKeydown({ key: "Enter", shiftKey: false, isComposing: false, repeat: false }), true);
});

test("Shift+Enter preserves a new line", () => {
  assert.equal(shouldSendOnKeydown({ key: "Enter", shiftKey: true, isComposing: false, repeat: false }), false);
});

test("IME composition and held-key repeats do not send", () => {
  assert.equal(shouldSendOnKeydown({ key: "Enter", shiftKey: false, isComposing: true, repeat: false }), false);
  assert.equal(shouldSendOnKeydown({ key: "Enter", shiftKey: false, isComposing: false, repeat: true }), false);
});
