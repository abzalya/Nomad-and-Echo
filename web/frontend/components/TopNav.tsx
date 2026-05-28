"use client";

import Link from "next/link";
import { IconGithub, IconHelp } from "./Icons";

export function TopNav({ onAbout }: { onAbout: () => void }) {
  return (
    <nav className="nav">
      <div className="nav-inner">
        <Link className="wordmark" href="/">
          chess<span className="accent">-room</span>
        </Link>
        <div className="nav-right">
          <button className="nav-link" onClick={onAbout} type="button">
            <IconHelp size={16} /> About
          </button>
          <a
            className="nav-link"
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
          >
            <IconGithub size={16} /> GitHub
          </a>
        </div>
      </div>
    </nav>
  );
}
