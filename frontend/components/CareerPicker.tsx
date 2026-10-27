"use client";

import { KeyboardEvent, useEffect, useId, useMemo, useRef, useState } from "react";
import { Career, SaTitle } from "@/lib/types";

const MAX_RESULTS = 60;

function normalize(text: string) {
  return text.toLowerCase().replace(/[^a-z0-9 ]+/g, " ").replace(/\s+/g, " ").trim();
}

export type CareerChoice = {
  slug: string; // career whose skills are scored
  title: string | null; // South African title, when one was picked
};

type Option = {
  key: string;
  label: string; // what the user sees and what goes on the certificate
  slug: string;
  saTitle: string | null;
  careerName: string;
  aliases: string[];
  description: string;
};

type Props = {
  id: string;
  careers: Career[];
  saTitles: SaTitle[];
  value: CareerChoice | null;
  onChange: (choice: CareerChoice | null) => void;
  loading?: boolean;
};

/**
 * Searchable career picker. Lists South African job titles (OFO 2021)
 * and the international (O*NET) career names they are scored against.
 * Type to filter, or open the list and scroll. Mouse, touch and keyboard.
 */
export function CareerPicker({ id, careers, saTitles, value, onChange, loading }: Props) {
  const listId = useId();
  const wrapperRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  const options = useMemo<Option[]>(() => {
    const bySlug = new Map(careers.map((c) => [c.slug, c]));
    const sa: Option[] = saTitles
      .filter((t) => bySlug.has(t.s))
      .map((t) => ({
        key: `sa:${t.t}:${t.s}`,
        label: t.t,
        slug: t.s,
        saTitle: t.t,
        careerName: bySlug.get(t.s)!.name,
        aliases: t.a || [],
        description: "",
      }));
    const intl: Option[] = careers.map((c) => ({
      key: `c:${c.slug}`,
      label: c.name,
      slug: c.slug,
      saTitle: null,
      careerName: c.name,
      aliases: [],
      description: c.description || "",
    }));
    return [...sa, ...intl].sort((a, b) => a.label.localeCompare(b.label));
  }, [careers, saTitles]);

  const indexed = useMemo(
    () =>
      options.map((o) => ({
        o,
        label: normalize(o.label),
        aliases: o.aliases.map(normalize),
        desc: normalize(o.description),
      })),
    [options]
  );

  const selected = value
    ? options.find((o) => o.slug === value.slug && o.saTitle === value.title) || null
    : null;

  const [query, setQuery] = useState(selected?.label ?? "");
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);

  // Show the chosen option's name; never wipe what the user is typing.
  useEffect(() => {
    if (selected?.label) setQuery(selected.label);
  }, [selected?.label]);

  const results = useMemo(() => {
    const q = normalize(query);
    if (!q || (selected && query === selected.label)) {
      return { items: indexed.slice(0, MAX_RESULTS).map((x) => ({ o: x.o, via: "" })), total: indexed.length };
    }
    const words = q.split(" ");
    const starts: { o: Option; via: string }[] = [];
    const inLabel: { o: Option; via: string }[] = [];
    const inAlias: { o: Option; via: string }[] = [];
    const inDesc: { o: Option; via: string }[] = [];
    for (const x of indexed) {
      if (words.every((w) => x.label.includes(w))) {
        if (x.label.startsWith(words[0]) || x.label.includes(" " + words[0])) starts.push({ o: x.o, via: "" });
        else inLabel.push({ o: x.o, via: "" });
        continue;
      }
      const ai = x.aliases.findIndex((a) => words.every((w) => a.includes(w)));
      if (ai >= 0) {
        inAlias.push({ o: x.o, via: x.o.aliases[ai] });
      } else if (x.desc && words.every((w) => x.desc.includes(w))) {
        inDesc.push({ o: x.o, via: "" });
      }
    }
    const all = [...starts, ...inLabel, ...inAlias, ...inDesc];
    return { items: all.slice(0, MAX_RESULTS), total: all.length };
  }, [query, indexed, selected]);

  useEffect(() => {
    setActive(0);
  }, [query]);

  useEffect(() => {
    function onDown(e: MouseEvent | TouchEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false);
        if (selected) setQuery(selected.label);
      }
    }
    document.addEventListener("mousedown", onDown);
    document.addEventListener("touchstart", onDown);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("touchstart", onDown);
    };
  }, [selected]);

  useEffect(() => {
    const el = listRef.current?.children[active] as HTMLElement | undefined;
    el?.scrollIntoView({ block: "nearest" });
  }, [active, open]);

  function choose(o: Option) {
    onChange({ slug: o.slug, title: o.saTitle });
    setQuery(o.label);
    setOpen(false);
  }

  function onKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setOpen(true);
      setActive((i) => Math.min(i + 1, results.items.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter") {
      if (open && results.items[active]) {
        e.preventDefault();
        choose(results.items[active].o);
      }
    } else if (e.key === "Escape") {
      setOpen(false);
      if (selected) setQuery(selected.label);
    }
  }

  return (
    <div ref={wrapperRef} className="relative">
      <div className="relative">
        <input
          id={id}
          type="text"
          role="combobox"
          aria-expanded={open}
          aria-controls={listId}
          aria-autocomplete="list"
          aria-activedescendant={open && results.items[active] ? `${listId}-${active}` : undefined}
          autoComplete="off"
          disabled={loading}
          value={query}
          placeholder={loading ? "Loading careers…" : 'Type a job title, e.g. "accounts clerk" or "nurse"'}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
            if (value) onChange(null);
          }}
          onFocus={(e) => {
            setOpen(true);
            e.target.select();
          }}
          onKeyDown={onKeyDown}
          className="focus-ring mt-1.5 w-full rounded-xl border border-line bg-white px-4 py-3 pr-10 font-body text-sm text-ink shadow-sm transition placeholder:text-slate-400 hover:border-brass"
        />
        <button
          type="button"
          tabIndex={-1}
          aria-label={open ? "Close career list" : "Show all careers"}
          onClick={() => setOpen((o) => !o)}
          className="absolute right-2 top-1/2 mt-[3px] -translate-y-1/2 rounded p-1.5 text-slate-500 hover:text-ink"
        >
          <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path d="M5.3 7.3a1 1 0 0 1 1.4 0L10 10.6l3.3-3.3a1 1 0 1 1 1.4 1.4l-4 4a1 1 0 0 1-1.4 0l-4-4a1 1 0 0 1 0-1.4z" />
          </svg>
        </button>
      </div>

      {open && !loading && (
        <div className="absolute z-20 mt-1 w-full overflow-hidden rounded-xl border border-line bg-white shadow-lg">
          {results.items.length === 0 ? (
            <p className="px-4 py-3 font-body text-sm text-slate-600">
              No career matches &ldquo;{query}&rdquo;. Try a shorter word, like &ldquo;nurse&rdquo; or &ldquo;clerk&rdquo;.
            </p>
          ) : (
            <ul ref={listRef} id={listId} role="listbox" className="max-h-80 overflow-y-auto py-1">
              {results.items.map(({ o, via }, i) => (
                <li
                  key={o.key}
                  id={`${listId}-${i}`}
                  role="option"
                  aria-selected={selected?.key === o.key}
                  onMouseEnter={() => setActive(i)}
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => choose(o)}
                  className={`cursor-pointer px-4 py-2 font-body ${i === active ? "bg-brass/15" : ""}`}
                >
                  <span className={`block text-sm text-ink ${selected?.key === o.key ? "font-medium" : ""}`}>
                    {o.label}
                  </span>
                  <span className="block text-xs text-slate-500">
                    {o.saTitle
                      ? `South Africa${via ? ` · also called ${via}` : ""} · skills of ${o.careerName}`
                      : "International (O*NET) occupation"}
                  </span>
                </li>
              ))}
            </ul>
          )}
          {results.total > results.items.length && (
            <p className="border-t border-line px-4 py-2 font-body text-xs text-slate-500">
              Showing {results.items.length} of {results.total}. Keep typing to narrow it down.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
