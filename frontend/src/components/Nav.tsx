"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/activities", label: "Aktivitäten" },
  { href: "/nutrition", label: "Ernährung" },
  { href: "/training", label: "Training" },
];

export default function Nav() {
  const path = usePathname();
  return (
    <nav className="nav" aria-label="Hauptnavigation">
      <div className="nav-inner">
        <span className="brand">Simfit</span>
        {LINKS.map((l) => {
          const active = l.href === "/" ? path === "/" : path.startsWith(l.href);
          return (
            <Link
              key={l.href}
              href={l.href}
              className={`link${active ? " active" : ""}`}
              aria-current={active ? "page" : undefined}
            >
              {l.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
