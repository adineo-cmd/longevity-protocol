export const site = {
  name: 'The Longevity Protocol',
  shortName: 'Longevity Protocol',
  url: 'https://adineo-cmd.github.io/longevity-protocol',
  tagline: 'One body, kept in working order.',
  description:
    'An evidence-graded operating manual for one body: biomarkers, hair, skin, sleep, nutrition and presence — every row carries its evidence grade and its source.',
  lastReviewed: 'October 2026',
  nav: [
    { href: '/longevity-protocol/systems/appearance', label: 'Appearance' },
    { href: '/longevity-protocol/systems/body-nutrition', label: 'Body & Nutrition' },
    { href: '/longevity-protocol/systems/sleep-recovery', label: 'Sleep' },
    { href: '/longevity-protocol/systems/longevity-health', label: 'Longevity' },
    { href: '/longevity-protocol/systems/presence-style', label: 'Presence' },
    { href: '/longevity-protocol/mistakes', label: 'Mistakes' },
    { href: '/longevity-protocol/plan', label: 'Plan' },
    { href: '/longevity-protocol/about', label: 'About' },
  ],
  footerNav: [
    { href: '/longevity-protocol/profile', label: 'Profile sheet' },
    { href: '/longevity-protocol/tracking', label: 'Tracking logs' },
    { href: '/longevity-protocol/plan', label: 'Twelve-week plan' },
    { href: '/longevity-protocol/about', label: 'Grades & references' },
  ],
  disclaimer:
    'Educational reference, not medical advice. Nothing here diagnoses or treats anything. Rows graded Rx are prescription-only: start, dose and stop belong to a clinician.',
};

export const gradeLegend = [
  { grade: 'A', label: 'multiple RCTs or a meta-analysis' },
  { grade: 'B', label: 'at least one RCT or a strong physiological case' },
  { grade: 'C', label: 'observational, mechanistic or expert consensus' },
  { grade: 'Rx', label: 'prescription-only — a clinician decides' },
];
