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

/* Brand palette, matching tailwind.config.js. */
const NAVY  = '#0a2540';
const STEEL = '#4a5c6f';
const SKY   = '#2aa3e8';
const MIST  = '#f4f7fa';
const LINE  = '#dde5ec';

const FONT = '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif';

// Who they are, versus what they are asking for. Split so the reply-to
// details sit at the top instead of buried in an alphabetical list.
const ENQUIRY_KEYS = ['sector', 'scope', 'site_address', 'height', 'sites', 'stage', 'timing'];

function val(fields, key) {
  return String(fields[key] || '').trim();
}

/* Email clients drop <style> blocks and anything resembling modern layout, so
   this is tables and inline styles throughout — verbose, but it survives. */
function asHtml(fields) {
  const name  = val(fields, 'name');
  const org   = val(fields, 'organisation');
  const role  = val(fields, 'role');
  const email = val(fields, 'email');
  const phone = val(fields, 'phone');
  const notes = val(fields, 'details');

  const title    = org || name || 'New enquiry';
  const subtitle = [name, role].filter(Boolean).join(' · ');

  let stamp;
  try {
    stamp = new Date().toLocaleString('en-AU', {
      timeZone: 'Australia/Brisbane',
      dateStyle: 'full',
      timeStyle: 'short',
    });
  } catch {
    stamp = new Date().toISOString();   // if the runtime ships without full ICU
  }

  // Zebra striping: the detail list is scanned, not read.
  let stripe = 0;
  const detailRows = ENQUIRY_KEYS.filter((k) => val(fields, k))
    .map((k) => {
      const bg = stripe++ % 2 ? '#ffffff' : MIST;
      return `<tr>
        <td bgcolor="${bg}" style="background:${bg};padding:11px 18px;border-bottom:1px solid ${LINE};color:${STEEL};font-size:13px;font-weight:600;white-space:nowrap;vertical-align:top">${escape(LABELS[k])}</td>
        <td bgcolor="${bg}" style="background:${bg};padding:11px 18px;border-bottom:1px solid ${LINE};color:${NAVY};font-size:15px;vertical-align:top">${escape(val(fields, k))}</td>
      </tr>`;
    })
    .join('');

  const contactLine = (label, value, href) => `<tr>
    <td style="padding:2px 0;color:${STEEL};font-size:13px;white-space:nowrap">${escape(label)}&nbsp;&nbsp;</td>
    <td style="padding:2px 0;font-size:16px;font-weight:600">
      ${href
        ? `<a href="${escape(href)}" style="color:${NAVY};text-decoration:none">${escape(value)}</a>`
        : `<span style="color:${NAVY}">${escape(value)}</span>`}
    </td>
  </tr>`;

  const contactRows = [
    email ? contactLine('Email', email, 'mailto:' + email) : '',
    phone ? contactLine('Phone', phone, 'tel:' + phone.replace(/[^\d+]/g, '')) : '',
  ].join('');

  return `<div style="margin:0;padding:0;background:${MIST}">
  <div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent">
    ${escape([title, val(fields, 'scope'), val(fields, 'sector')].filter(Boolean).join(' — '))}
  </div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${MIST}" style="background:${MIST};padding:28px 12px">
    <tr><td align="center">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="640" style="width:100%;max-width:640px;background:#ffffff;border:1px solid ${LINE};border-radius:10px;overflow:hidden;font-family:${FONT}">

        <tr><td bgcolor="${NAVY}" style="background:${NAVY};padding:26px 28px">
          <p style="margin:0 0 8px;color:${SKY};font-size:11.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase">
            Altitude &mdash; website enquiry
          </p>
          <h1 style="margin:0;color:#ffffff;font-size:23px;font-weight:600;line-height:1.25">${escape(title)}</h1>
          ${subtitle ? `<p style="margin:7px 0 0;color:rgba(255,255,255,.72);font-size:14.5px">${escape(subtitle)}</p>` : ''}
        </td></tr>

        ${contactRows ? `<tr><td style="padding:22px 28px 4px">
          <table role="presentation" cellpadding="0" cellspacing="0" border="0">${contactRows}</table>
        </td></tr>` : ''}

        ${detailRows ? `<tr><td style="padding:20px 28px 0">
          <p style="margin:0 0 10px;color:${STEEL};font-size:11.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase">Enquiry</p>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border:1px solid ${LINE};border-radius:8px;border-collapse:separate;overflow:hidden">${detailRows}</table>
        </td></tr>` : ''}

        ${notes ? `<tr><td style="padding:20px 28px 0">
          <p style="margin:0 0 10px;color:${STEEL};font-size:11.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase">Notes</p>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr><td style="border-left:3px solid ${SKY};padding:2px 0 2px 14px;color:${NAVY};font-size:15px;line-height:1.6">${escape(notes).replace(/\n/g, '<br>')}</td></tr>
          </table>
        </td></tr>` : ''}

        ${email ? `<tr><td style="padding:26px 28px 28px">
          <a href="mailto:${escape(email)}" style="display:inline-block;background:${NAVY};color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;padding:13px 26px;border-radius:6px">
            Reply to ${escape(name || 'enquirer')}
          </a>
        </td></tr>` : ''}

        <tr><td bgcolor="${MIST}" style="background:${MIST};border-top:1px solid ${LINE};padding:16px 28px;color:${STEEL};font-size:12.5px;line-height:1.6">
          Received ${escape(stamp)}.<br>
          Replying to this email goes straight back to the enquirer.
        </td></tr>

      </table>
      <p style="margin:16px 0 0;color:${STEEL};font-size:11.5px;font-family:${FONT}">
        Sent by the enquiry form at altitudedroneexteriorcleaning.com
      </p>
    </td></tr>
  </table>
</div>`;
}

function escape(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
