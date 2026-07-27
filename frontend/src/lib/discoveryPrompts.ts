export const HERO_EXAMPLES = [
  "🍝 I'm making pasta tonight",
  "🎉 Planning a house party",
  "🎁 Gift for my best friend",
  "💕 Date night at home",
  "💄 Build my makeup routine",
  "🥗 Healthy breakfast ideas",
  "👶 Newborn essentials",
  "🐶 Dog food for my puppy",
  "🏕️ Weekend picnic",
  "🏠 Monthly household refill",
] as const;

export type PopularChip = {
  label: string;
  prompt: string;
};

/** Shown on the home hero and discover tab — horizontally scrollable intent chips. */
export const POPULAR_CHIPS: PopularChip[] = [
  { label: "🍝 Pasta Night", prompt: "I'm making pasta tonight." },
  { label: "🎁 Gift Ideas", prompt: "Gift ideas for my best friend" },
  { label: "💄 Makeup Routine", prompt: "Build my makeup routine" },
  { label: "💕 Date Night", prompt: "Date night at home" },
  { label: "🎉 House Party", prompt: "Planning a house party" },
  { label: "🏋️ High Protein", prompt: "High protein gym snacks and meals" },
  { label: "👶 Baby Essentials", prompt: "Newborn baby essentials" },
  { label: "🐶 Pet Care", prompt: "Dog food and pet care essentials" },
  { label: "🏠 Monthly Refill", prompt: "Monthly household refill" },
  { label: "🍿 Movie Night", prompt: "Movie night snacks and drinks" },
  { label: "🧳 Travel Kit", prompt: "Travel essentials kit" },
  { label: "🥗 Healthy Eating", prompt: "Healthy eating and breakfast ideas" },
  { label: "☕ Coffee Break", prompt: "Coffee break snacks and drinks" },
  { label: "🥘 Dinner for 4", prompt: "Dinner for 4 people tonight" },
];

export const DISCOVERY_INPUT_PLACEHOLDER = "What are you shopping for today?";

export function chipLabelToDisplay(label: string): string {
  return label.replace(/^[^\s]+\s/, "").trim();
}
