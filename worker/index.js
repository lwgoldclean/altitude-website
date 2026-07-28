/**
 * Altitude enquiry-form relay.
 *
 * A static site on GitHub Pages cannot hold a Resend API key — anything in the
 * page source is public, and a leaked key lets a stranger send mail as your
 * domain. This Worker sits between the form and Resend so the key stays server
 * side. It is the smallest piece of backend that makes the form work.
 *
 * Deploy:  npx wrangler deploy
 * Secret:  npx wrangler secret put RESEND_API_KEY
 */

/* Deliberately minimal. Every additional mandatory field costs enquiries, and
   a name and a reply address are all that is needed to respond — the rest of
   the form is there for people who want to give it. */
const REQUIRED = ['name', 'email'];

export default {
  async fetch(request, env) {
    const origin = env.ALLOWED_ORIGIN || '*';

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors(origin) });
    }
    if (request.method !== 'POST') {
      return json({ success: false, message: 'Method not allowed' }, 405, origin);
    }

    let fields;
    try {
      fields = await readFields(request);
    } catch {
      return json({ success: false, message: 'Could not read submission' }, 400, origin);
    }

    // Honeypot: hidden from real users, routinely filled in by bots.
    if (fields.botcheck) {
      return json({ success: true }, 200, origin); // accept silently, send nothing
    }

    const missing = REQUIRED.filter((f) => !String(fields[f] || '').trim());
    if (missing.length) {
      return json(
        { success: false, message: `Missing required field: ${missing.join(', ')}` },
        400,
        origin
      );
    }

    const enquirerEmail = String(fields.email).trim();
    const subject = fields.subject
      ? String(fields.subject)
      : `Website enquiry — ${fields.organisation || fields.name}`;

    const sent = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: env.FROM_EMAIL,
        to: [env.TO_EMAIL],
        subject,
        // Replying in your mail client goes straight back to the enquirer.
        reply_to: isEmail(enquirerEmail) ? enquirerEmail : undefined,
        text: asText(fields),
        html: asHtml(fields),
      }),
    });

    if (!sent.ok) {
      const detail = await sent.text();
      console.error('Resend rejected the send:', sent.status, detail);
      return json(
        { success: false, message: 'Email service rejected the request' },
        502,
        origin
      );
    }

    return json({ success: true }, 200, origin);
  },
};

/* ---------- helpers ---------- */

function cors(origin) {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Accept',
    'Access-Control-Max-Age': '86400',
  };
}

function json(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json', ...cors(origin) },
  });
}

async function readFields(request) {
  const type = request.headers.get('content-type') || '';
  if (type.includes('application/json')) return await request.json();
  const form = await request.formData();
  return Object.fromEntries(form.entries());
}

function isEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

// Presentation order matters — this is what lands in the inbox.
const LABELS = {
  organisation: 'Organisation',
  name: 'Contact name',
  role: 'Role',
  sector: 'Sector',
  email: 'Email',
  phone: 'Phone',
  site_address: 'Site address',
  scope: 'Scope',
  height: 'Building height',
  sites: 'Sites',
  stage: 'Procurement stage',
  timing: 'Timing',
  details: 'Notes',
};

function entries(fields) {
  return Object.keys(LABELS)
    .filter((key) => String(fields[key] || '').trim())
    .map((key) => [LABELS[key], String(fields[key]).trim()]);
}

function asText(fields) {
  const lines = entries(fields).map(([label, value]) => `${label}: ${value}`);
  return `New enquiry from altitudedroneexteriorcleaning.com\n\n${lines.join('\n')}\n`;
}

function asHtml(fields) {
  const rows = entries(fields)
    .map(
      ([label, value]) =>
        `<tr>
           <th align="left" style="padding:8px 16px 8px 0;vertical-align:top;color:#4a5c6f;font-weight:600;white-space:nowrap">${escape(label)}</th>
           <td style="padding:8px 0;vertical-align:top;color:#0a2540">${escape(value).replace(/\n/g, '<br>')}</td>
         </tr>`
    )
    .join('');

  return `<div style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;max-width:640px">
    <p style="font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:#12608f;margin:0 0 4px">
      Altitude — website enquiry
    </p>
    <h1 style="font-size:20px;color:#0a2540;margin:0 0 20px">
      ${escape(fields.organisation || fields.name || 'New enquiry')}
    </h1>
    <table style="border-collapse:collapse;font-size:15px;line-height:1.5">${rows}</table>
    <p style="margin-top:24px;font-size:13px;color:#4a5c6f">
      Reply to this email to respond directly to the enquirer.
    </p>
  </div>`;
}

function escape(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
