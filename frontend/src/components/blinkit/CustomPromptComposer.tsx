"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles } from "lucide-react";

export default function CustomPromptComposer() {
  const router = useRouter();
  const [value, setValue] = useState("");

  function submit() {
    const text = value.trim();
    if (text) {
      router.push(`/discover?prompt=${encodeURIComponent(text)}`);
    } else {
      router.push("/discover");
    }
  }

  return (
    <section
      className="mx-4 animate-[fadeInUp_0.6s_ease-out] rounded-[20px] border border-zinc-100 bg-white p-4 shadow-card"
      aria-labelledby="custom-prompt-title"
    >
      <h2 id="custom-prompt-title" className="text-sm font-bold text-zinc-800">
        Or tell us what you need
      </h2>
      <label className="sr-only" htmlFor="home-custom-prompt">
        Describe what you need
      </label>
      <textarea
        id="home-custom-prompt"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Type anything..."
        rows={3}
        className="mt-3 w-full resize-none rounded-xl border border-zinc-200 bg-zinc-50/80 px-3 py-2.5 text-sm text-zinc-800 placeholder:text-zinc-400 focus:border-blinkit-green focus:bg-white focus:outline-none focus:ring-2 focus:ring-blinkit-green/20"
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit();
          }
        }}
      />
      <p className="mt-2 text-[11px] leading-relaxed text-zinc-500">
        Examples: Dinner for 4 · Gift under ₹1000 · Makeup for oily skin · Birthday party supplies
      </p>
      <button
        type="button"
        onClick={submit}
        className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl bg-blinkit-green py-3 text-sm font-bold text-white shadow-md transition hover:bg-blinkit-green-dark active:scale-[0.99]"
      >
        <Sparkles className="h-4 w-4" aria-hidden />
        Discover
      </button>
    </section>
  );
}
