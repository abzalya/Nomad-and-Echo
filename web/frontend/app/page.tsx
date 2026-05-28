"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { TopNav } from "@/components/TopNav";
import { DecorativeBoard, LANDING_FEN } from "@/components/DecorativeBoard";
import { BotCard } from "@/components/BotCard";
import { AboutModal } from "@/components/Modals";
import { IconArrowRight } from "@/components/Icons";

const WELCOME_KEY = "seen_welcome";

export default function LandingPage() {
  const router = useRouter();
  const [aboutOpen, setAboutOpen] = useState(false);
  const [welcomeOpen, setWelcomeOpen] = useState(false);

  useEffect(() => {
    try {
      if (!localStorage.getItem(WELCOME_KEY)) setWelcomeOpen(true);
    } catch {}
  }, []);

  const dismissWelcome = () => {
    setWelcomeOpen(false);
    try {
      localStorage.setItem(WELCOME_KEY, "1");
    } catch {}
  };

  return (
    <>
      <TopNav onAbout={() => setAboutOpen(true)} />
      <div className="page landing">
        <section className="landing-hero">
          <div className="landing-hero-text">
            <div className="eyebrow mono text-xs">A portfolio piece</div>
            <h1 className="landing-headline text-2xl weight-700">
              Play chess against a custom engine{" "}
              <span className="muted">— or a clone of its developer.</span>
            </h1>
            <p className="landing-sub text-xl muted weight-400">
              Built from scratch in Python. Two opponents, one board.
            </p>
            <div className="landing-cta row gap-16">
              <button
                className="btn btn-primary btn-lg"
                onClick={() => router.push("/play")}
                type="button"
              >
                Play
                <IconArrowRight size={18} />
              </button>
              <button
                className="btn btn-ghost"
                onClick={() => setAboutOpen(true)}
                type="button"
              >
                How it works
              </button>
            </div>
            <div className="landing-meta row gap-24 text-xs muted mono">
              <span>
                <span className="pip" /> &nbsp; engine online
              </span>
              <span>v0.1.0</span>
              <span>self-hosted</span>
            </div>
          </div>

          <div className="landing-board-wrap">
            <div className="landing-board-glow" />
            <DecorativeBoard fen={LANDING_FEN} orientation="black" />
            <div className="landing-board-caption mono text-xs muted">
              R+P vs R+2P · black to move
            </div>
          </div>
        </section>

        <section className="landing-bots">
          <BotCard
            bot="nomad"
            title="Nomad"
            tagline="The engine. Bitboards, alpha-beta, transposition tables. Plays at full strength."
            tech={["bitboards", "alpha-beta", "TT", "null-move", "LMR"]}
            onPlay={() => router.push("/play?opponent=nomad")}
          />
          <BotCard
            bot="echo"
            title="Echo"
            tagline="The mimic. Trained on the developer's own games. Plays in their style — for better or worse."
            tech={["mimic", "experimental", "~1500"]}
            onPlay={() => router.push("/play?opponent=echo")}
          />
        </section>
      </div>

      {welcomeOpen && (
        <AboutModal variant="welcome" onClose={dismissWelcome} />
      )}
      {aboutOpen && !welcomeOpen && (
        <AboutModal variant="about" onClose={() => setAboutOpen(false)} />
      )}
    </>
  );
}
