export type Kit = "owned" | "available";
export const bodies = [
    {
        id: "r7",
        name: "EOS R7",
        type: "Mirrorless",
        sensor: "32.5 MP · APS-C",
        kit: "owned",
    },
    {
        id: "40d",
        name: "EOS 40D",
        type: "DSLR",
        sensor: "10.1 MP · APS-C",
        kit: "owned",
    },
    {
        id: "c200",
        name: "Cinema EOS C200",
        type: "Cinema camera",
        sensor: "Super 35 · 4K",
        kit: "available",
    },
] as const;
export const lenses = [
    {
        id: "28-135",
        name: "EF 28–135mm",
        detail: "IS USM",
        aperture: "f/3.5–5.6",
        range: "28–135mm",
        kit: "owned",
        white: false,
    },
    {
        id: "70-200-f4",
        name: "EF 70–200mm",
        detail: "f/4L IS USM",
        aperture: "f/4",
        range: "70–200mm",
        kit: "owned",
        white: true,
    },
    {
        id: "35",
        name: "Tamron SP 35mm",
        detail: "f/1.4 Di USD",
        aperture: "f/1.4",
        range: "35mm",
        kit: "owned",
        white: false,
    },
    {
        id: "50",
        name: "EF 50mm",
        detail: "f/1.8 II",
        aperture: "f/1.8",
        range: "50mm",
        kit: "owned",
        white: false,
    },
    {
        id: "70-200-f28",
        name: "EF 70–200mm",
        detail: "f/2.8 · Example setup",
        aperture: "f/2.8",
        range: "70–200mm",
        kit: "available",
        white: true,
    },
] as const;
export type Body = (typeof bodies)[number];
export type Lens = (typeof lenses)[number];
