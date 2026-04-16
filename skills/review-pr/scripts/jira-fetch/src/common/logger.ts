type Meta = Record<string, unknown> | undefined;

const formatMeta = (meta: Meta): string => {
  if (!meta) {
    return '';
  }

  try {
    return ` ${JSON.stringify(meta)}`;
  } catch {
    return '';
  }
};

export const logger = {
  info(message: string, meta?: Meta): void {
    process.stdout.write(`[revew-pr] ${message}${formatMeta(meta)}\n`);
  },
  error(message: string, meta?: Meta): void {
    process.stderr.write(`[revew-pr] ${message}${formatMeta(meta)}\n`);
  },
};
