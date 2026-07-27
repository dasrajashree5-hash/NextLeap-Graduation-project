"use client";

import { ChevronDown, MapPin, User } from "lucide-react";

type Props = {
  deliveryMinutes?: number;
};

export default function MobileHeader({ deliveryMinutes = 11 }: Props) {
  return (
    <header className="bg-blinkit px-4 pb-2 pt-3 text-blinkit-ink">
      <p className="text-lg font-black tracking-tight">blinkit</p>
      <div className="mt-2 flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className="text-[10px] font-semibold uppercase tracking-wide opacity-80">
            Delivery in {deliveryMinutes} minutes
          </p>
          <button
            type="button"
            className="mt-0.5 flex max-w-full items-center gap-1 text-left"
            aria-label="Change delivery location"
          >
            <MapPin className="h-4 w-4 flex-shrink-0" aria-hidden />
            <span className="truncate text-sm font-bold">Home · Koramangala 5th Block</span>
            <ChevronDown className="h-4 w-4 flex-shrink-0 opacity-70" aria-hidden />
          </button>
        </div>
        <button
          type="button"
          className="flex h-9 w-9 items-center justify-center rounded-full bg-black/10"
          aria-label="Account"
        >
          <User className="h-5 w-5" aria-hidden />
        </button>
      </div>
    </header>
  );
}
