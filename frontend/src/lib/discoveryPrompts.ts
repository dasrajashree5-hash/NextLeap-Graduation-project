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

export const POPULAR_CHIPS: PopularChip[] = [
  { label: "🍝 Pasta Night", prompt: "I'm making pasta tonight." },
  { label: "🎉 House Party", prompt: "Planning a house party" },
  { label: "🎁 Gifts", prompt: "Gift for my best friend" },
  { label: "💄 Makeup", prompt: "Build my makeup routine" },
  { label: "💕 Date Night", prompt: "Date night at home" },
  { label: "🥗 Healthy Eating", prompt: "Healthy breakfast ideas" },
  { label: "👶 Baby Care", prompt: "Newborn essentials" },
  { label: "🐶 Pet Care", prompt: "Dog food for my puppy" },
  { label: "🏠 Home Essentials", prompt: "Monthly household refill" },
  { label: "🏋️ Gym Snacks", prompt: "Gym snacks and protein picks" },
  { label: "✈️ Travel Kit", prompt: "Travel essentials kit" },
  { label: "🍿 Movie Night", prompt: "Movie night snacks and drinks" },
];

export function chipLabelToDisplay(label: string): string {
  return label.replace(/^[^\s]+\s/, "").trim();
}
