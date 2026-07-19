import { registerRoot } from "remotion";
import { RemotionRoot } from "./Root";
import { createRoot } from "react-dom/client";
import React from "react";

if (typeof window !== "undefined" && window.location.search.includes("mode=persistent")) {
  const container = document.getElementById("video-container");
  if (container) {
    const root = createRoot(container);
    root.render(React.createElement(RemotionRoot));
  } else {
    console.error("Could not find video-container element");
  }
} else {
  registerRoot(RemotionRoot);
}
