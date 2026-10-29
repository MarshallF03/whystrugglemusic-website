# Pointing whystrugglemusic.com at GitHub Pages

The domain is at Fasthosts. In the Fasthosts control panel, open the domain, go to DNS settings, and make these changes. Leave every other record alone (especially MX records once email is set up).

## Records to set

Delete the existing A record for the bare domain (`@`) that points to `213.171.195.105` (Fasthosts parking page), and the existing `www` A record pointing to the same address. Then add:

| Type  | Name  | Value                   |
|-------|-------|-------------------------|
| A     | @     | 185.199.108.153         |
| A     | @     | 185.199.109.153         |
| A     | @     | 185.199.110.153         |
| A     | @     | 185.199.111.153         |
| CNAME | www   | marshallf03.github.io   |

Optional IPv6 (AAAA) records for `@`: 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153.

## After DNS updates

1. Changes can take from a few minutes to a few hours.
2. GitHub then issues a free HTTPS certificate automatically.
3. Once the certificate is ready, turn on "Enforce HTTPS" in the repo's Settings, then Pages.

## Later

- Shop: add a CNAME record for `shop` pointing wherever the shop platform (for example Payhip) tells you. This doesn't touch the main site.
- Email addresses (contact@, support@, artistservices@, bradley@) are set up in Fasthosts and use MX records. They don't affect the website.
