export const DEFAULT_SETTINGS = {
  theme: { color: 'blue', density: 'normal' },
  notifications: { email: true, sms: false },
  locale: 'en',
};

function merge(target, source) {
  for (const key in source) {
    const value = source[key];
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      if (!target[key]) target[key] = {};
      merge(target[key], value);
    } else {
      target[key] = value;
    }
  }
  return target;
}

// body is the raw JSON request body a customer sent to PUT /settings.
export function applyUserSettings(defaults, body) {
  return merge(merge({}, defaults), JSON.parse(body));
}
