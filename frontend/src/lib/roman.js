// Convert 1..3999 to a Roman numeral (used for the year/level cards).
const MAP = [
  [1000, "M"], [900, "CM"], [500, "D"], [400, "CD"],
  [100, "C"], [90, "XC"], [50, "L"], [40, "XL"],
  [10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"],
];

export function toRoman(num) {
  let n = Number(num);
  if (!Number.isFinite(n) || n <= 0) return String(num ?? "");
  let out = "";
  for (const [value, sym] of MAP) {
    while (n >= value) {
      out += sym;
      n -= value;
    }
  }
  return out;
}
