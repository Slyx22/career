"use client";

import { KeyboardEvent, useEffect, useId, useMemo, useRef, useState } from "react";
import { Career } from "@/lib/types";

const MAX_RESULTS = 60;

function normalize(text: string) {
  return text.toLowerCase().replace(/[^a-z0-9 ]+/g, " ").replace(/\s+/g, " ").trim();
}

type Props = {
  id: string;
  careers: Career[];
  value: string; // selected career slug, "" when none
  onChange: (slug: string) => void;
  loading?: boolean;
};

/**
 * Searchable career picker: type to filter (by job title, then by
 * description), or open the list and scroll. Works with mouse, touch and
 * keyboard (arrow keys, Enter, Escape).
 */
export function CareerPicker({ id, careers, value, onChange, loading }: Props) {
  const listId = useId();
  const wrapperRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const selected = careers.find((c) => c.slug === value) || null;

  const [query, setQuery] = useState(selected?.name ?? "");
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);

  // When a career gets selected (or the list loads with one selected),
  // show its name. Clearing the selection while typing must not wipe
  // what the user is typing, so only sync when there is a selection.
  useEffect(() => {
    if (selected?.name) setQuery(selected.name);
  }, [selected?.name]);

  const indexed = useMemo(
    () => careers.map((c) => ({ career: c, name: normalize(c.name), desc: normalize(c.description || "") })),
    [careers]
  );

  const results = useMemo(() => {
    const q = normalize(query);
    // Showing the chosen career's full name means "no filter yet".
    if (!q || (selected && query === selected.name)) {
      return { items: indexed.slice(0, MAX_RESULTS).map((x) => x.career), total: indexed.length };
    }
    const words = q.split(" ");
    const starts: Career[] = [];
    const inName: Career[] = [];
    const inDesc: Career[] = [];
    for (const x of indexed) {
      if (words.every((w) => x.name.includes(w))) {
        if (x.name.startsWith(words[0]) || x.name.includes(" " + words[0])) starts.push(x.career);
        else inName.push(x.career);
      } else if (words.every((w) => x.desc.includes(w))) {
        inDesc.push(x.career);
      }
    }
    const all = [...starts, ...inName, ...inDesc];
    return { items: all.slice(0, MAX_RESULTS), total: all.length };
  }, [query, indexed, selected]);

  useEffect(() => {
    setActive(0);
  }, [query]);

  // Close when clicking outside.
  useEffect(() => {
    function onDown(e: MouseEvent | TouchEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false);
        setQuery(selected?.name ?? "");
      }
    }
    document.addEventListener("mousedown", onDown);
    document.addEventListener("touchstart", onDown);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("touchstart", onDown);
    };
  }, [selected?.name]);

  // Keep the highlighted option in view.
  useEffect(() => {
    const el = listRef.current?.children[active] as HTMLElement | undefined;
    el?.scrollIntoView({ block: "nearest" });
  }, [active, open]);

  function choose(c: Career) {
    onChange(c.slug);
    setQuery(c.name);
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
        choose(results.items[active]);
      }
    } else if (e.key === "Escape") {
      setOpen(false);
      setQuery(selected?.name ?? "");
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
          placeholder={loading ? "Loading careers…" : `Type a job title, e.g. "accountant" (${careers.length} careers)`}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
            if (value) onChange("");
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
            <ul ref={listRef} id={listId} role="listbox" className="max-h-72 overflow-y-auto py-1">
              {results.items.map((c, i) => (
                <li
                  key={c.slug}
                  id={`${listId}-${i}`}
                  role="option"
                  aria-selected={c.slug === value}
                  onMouseEnter={() => setActive(i)}
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => choose(c)}
                  className={`cursor-pointer px-4 py-2 font-body text-sm ${
                    i === active ? "bg-brass/15 text-ink" : "text-ink"
                  } ${c.slug === value ? "font-medium" : ""}`}
                >
                  {c.name}
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
