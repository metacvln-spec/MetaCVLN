export default function MetaPublic() {
  const entities = [
    { name: "FREKCORE", tag: "Trust Anchor", desc: "Preuve musicale offline, Ed25519 · sans surveillance" },
    { name: "FREKANSLA", tag: "Master Certifier", desc: "FK Object v3, provenance signée" },
    { name: "Agent Factory", tag: "Control Plane", desc: "Fabrique d'agents spécialisés" },
    { name: "Laurent.ia", tag: "Sovereign AI", desc: "Décision souveraine diasporique, BSL 1.1" },
    { name: "CVL Academy", tag: "Learning", desc: "Formation, certification, recherche" },
    { name: "Kiltikonet", tag: "Culture Connect", desc: "Écosystème culturel Martinique 2026" },
    { name: "Gala Cook & Food", tag: "Event", desc: "Gala culinaire Paris 12.12.2026" },
    { name: "Factory Maker Studio", tag: "LabelOS", desc: "Label, production, catalogue musical" },
    { name: "CVLN Wallet", tag: "Value Layer", desc: "Transferts notarisés cross-entités" },
    { name: "Command Center", tag: "Orchestration", desc: "Classify · route · alert" },
    { name: "Factory Ops", tag: "Studio Ops", desc: "Sessions, plannings, réservations" },
    { name: "Production Vault", tag: "Sovereign Storage", desc: "Coffre-fort de masters & contrats" },
  ];

  return (
    <div className="min-h-screen bg-[#08090C] text-white" data-testid="meta-public-page">
      <div className="border-b border-[#252633] px-8 py-4 flex items-center justify-between sticky top-0 bg-[#08090C]/95 backdrop-blur z-40">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-sm bg-gradient-to-br from-violet-500 to-violet-800" />
          <div>
            <div className="label-cap">CVLN</div>
            <div className="font-mono text-xs tracking-widest">META · CVLN <span className="text-violet-400">PUBLIC</span></div>
          </div>
        </div>
        <div className="flex items-center gap-6 label-cap">
          <a href="#ecosystem" className="hover:text-white">Écosystème</a>
          <a href="#doctrine" className="hover:text-white">Doctrine</a>
          <a href="#partners" className="hover:text-white">Partenaires</a>
          <a href="/commercial" className="hover:text-white">Commercial</a>
          <a href="/audit" className="hover:text-amber-400">Notary audit</a>
          <a href="/login" className="btn-ghost text-[10px]">Accès interne</a>
        </div>
      </div>

      {/* Hero */}
      <section className="px-8 py-24 max-w-6xl relative grain-overlay">
        <div className="label-cap">Public ecosystem interface</div>
        <h1 className="text-5xl md:text-7xl font-semibold tracking-tight mt-4 leading-none">
          One ecosystem. <br />
          <span className="text-violet-400">Many intelligences.</span>
        </h1>
        <p className="text-base text-white/60 mt-8 max-w-2xl leading-relaxed">
          Meta CVLN connecte, comprend, orchestre et sécurise 12 systèmes indépendants pour créer
          une intelligence collective. Chaque événement est notarisé Ed25519, vérifiable par un tiers,
          sans surveillance et sans plateforme centralisatrice.
        </p>
        <div className="mt-10 flex gap-3 flex-wrap">
          <a href="/audit" data-testid="cta-audit" className="btn-gold">Voir la trust chain publique</a>
          <a href="#ecosystem" data-testid="cta-eco" className="btn-ghost">Découvrir l'écosystème</a>
          <a href="#founder" data-testid="cta-founder" className="btn-ghost">Vision du fondateur</a>
        </div>
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl">
          <div className="border border-[#252633] rounded-sm p-4"><div className="kpi-value text-2xl">12</div><div className="label-cap mt-1">Entités connectées</div></div>
          <div className="border border-[#252633] rounded-sm p-4"><div className="kpi-value text-2xl text-emerald-400">100%</div><div className="label-cap mt-1">CONNECTED · 24h</div></div>
          <div className="border border-[#252633] rounded-sm p-4"><div className="kpi-value text-2xl text-amber-400">Ed25519</div><div className="label-cap mt-1">Trust protocol</div></div>
          <div className="border border-[#252633] rounded-sm p-4"><div className="kpi-value text-2xl text-violet-300">.FK</div><div className="label-cap mt-1">Signed containers</div></div>
        </div>
      </section>

      {/* Founder narrative */}
      <section id="founder" className="border-t border-[#252633] px-8 py-20 max-w-4xl">
        <div className="label-cap mb-4">Vision · Fondateur</div>
        <blockquote className="text-2xl md:text-3xl font-semibold text-white leading-tight">
          « Nous ne construisons pas une plateforme. Nous construisons la couche qui permet
          à des systèmes souverains de rester souverains — <span className="text-violet-400">tout en agissant ensemble</span>. »
        </blockquote>
        <div className="label-cap mt-6">— Anba Tolm, CVLN Group Holding</div>
        <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-white/70">
          <div>
            <div className="label-cap text-amber-400 mb-2">Doctrine</div>
            Data → Context → Decision → Verification → Feedback. L'humain reste au centre.
            Aucune décision critique automatisée sans validation.
          </div>
          <div>
            <div className="label-cap text-amber-400 mb-2">Souveraineté</div>
            Chaque entité conserve son code, ses données, ses règles. Meta CVLN n'orchestre
            que la coopération — jamais la substitution.
          </div>
          <div>
            <div className="label-cap text-amber-400 mb-2">Preuve</div>
            Chaque ping, chaque événement, chaque décision produit une preuve cryptographique
            au format FK signé Ed25519.
          </div>
        </div>
      </section>

      {/* FREKCORE spotlight */}
      <section id="doctrine" className="border-t border-[#252633] px-8 py-20 max-w-6xl">
        <div className="label-cap mb-4">Focus actuel · Programme FREKCORE</div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-start">
          <div>
            <h2 className="text-3xl font-semibold text-white leading-tight">
              L'intelligence collective des systèmes commence par la <span className="text-amber-400">preuve</span>.
            </h2>
            <p className="text-sm text-white/60 mt-5 leading-relaxed">
              FREKCORE est le standard ouvert de preuve musicale de CVLN. Vérification en navigateur,
              signature Ed25519, format `.frek.json` pour la preuve d'origine, format `.FK` (FREKANSLA)
              pour les conteneurs signés de provenance. Aucun serveur central. Aucune surveillance.
            </p>
            <ul className="text-sm text-white/70 mt-6 space-y-2">
              <li>· FREK ne juge pas la musique</li>
              <li>· FREK ne classe pas les artistes</li>
              <li>· FREK ne collecte pas de données personnelles</li>
              <li>· FREK ne devient jamais une plateforme</li>
              <li>· FREK fonctionne offline par défaut</li>
            </ul>
          </div>
          <div className="border border-[#252633] rounded-sm p-6 font-mono text-xs">
            <div className="label-cap text-violet-300 mb-3">.fk container · FK Object v3</div>
            <pre className="text-white/70 leading-relaxed whitespace-pre-wrap">{`{
  "fk_version": "3.0",
  "issuer": "meta-cvln-os",
  "event": { "target_repo": "kiltikonet", "status": "CONNECTED" },
  "fingerprint": { "algorithm": "sha256", "value": "af369fb0..." },
  "signature":   { "algorithm": "ed25519", "value": "ExOOfc4oW..." },
  "notary": { "did": "did:meta-cvln:413ba83b...", "source": "local" }
}`}</pre>
          </div>
        </div>
      </section>

      {/* Ecosystem grid */}
      <section id="ecosystem" className="border-t border-[#252633] px-8 py-20">
        <div className="label-cap mb-6">L'écosystème CVLN — 12 entités connectées & notarisées</div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 max-w-7xl">
          {entities.map((e) => (
            <div key={e.name} className="border border-[#252633] rounded-sm p-5 hover:border-violet-500/60 transition-colors">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                <span className="label-cap text-amber-400">{e.tag}</span>
              </div>
              <div className="text-lg text-white font-semibold">{e.name}</div>
              <div className="text-xs text-white/60 mt-2 leading-relaxed">{e.desc}</div>
              <div className="label-cap mt-4 text-emerald-400">CONNECTED · NOTARIZED</div>
            </div>
          ))}
        </div>
      </section>

      {/* Partners */}
      <section id="partners" className="border-t border-[#252633] px-8 py-20 max-w-6xl">
        <div className="label-cap mb-6">Ils accompagnent CVLN</div>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          {["TRACE", "SACEM", "CNM", "France Travail", "Google for Startups", "AWS"].map((p) => (
            <div key={p} className="border border-[#252633] rounded-sm p-6 flex items-center justify-center text-white/70 font-semibold hover:border-amber-500/50 transition-colors">{p}</div>
          ))}
        </div>
      </section>

      {/* Community CTA */}
      <section className="border-t border-[#252633] px-8 py-20">
        <div className="max-w-4xl">
          <div className="label-cap mb-3">Rejoindre la communauté</div>
          <h2 className="text-4xl font-semibold text-white leading-tight">
            Construisons ensemble <span className="text-violet-400">l'héritage du futur.</span>
          </h2>
          <p className="text-sm text-white/60 mt-4 max-w-2xl">
            CVLN est une communauté de créateurs, développeurs, chercheurs et institutions qui refusent
            la centralisation. Chaque contribution renforce la trust chain.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a href="/commercial" data-testid="cta-partner" className="btn-gold">Devenir partenaire</a>
            <a href="/audit" data-testid="cta-verify" className="btn-ghost">Vérifier la trust chain</a>
            <a href="mailto:hello@cvln" data-testid="cta-contact" className="btn-ghost">Nous écrire</a>
          </div>
        </div>
      </section>

      <footer className="border-t border-[#252633] px-8 py-8 label-cap text-white/40">
        CVLN Group · Fondation · OS interne · Commercial · Public — construits ensemble, séparés par doctrine.
      </footer>
    </div>
  );
}
