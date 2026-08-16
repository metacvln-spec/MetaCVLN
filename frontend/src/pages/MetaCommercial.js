export default function MetaCommercial() {
  const offers = [
    { name: "Starter", price: "Gratuit", perks: ["Accès API essentielles", "Monitoring de base"] },
    { name: "Pro", price: "€499/mois", perks: ["Orchestration avancée", "Agents spécialisés", "Support prioritaire"] },
    { name: "Enterprise", price: "Sur devis", perks: ["Solution complète", "SLA & support dédié", "Notarisation Ed25519"] },
    { name: "On-Premise", price: "Sur devis", perks: ["Déploiement privé", "Contrôle total"] },
  ];
  return (
    <div className="min-h-screen bg-[#08090C] text-white" data-testid="meta-commercial-page">
      <div className="border-b border-[#252633] px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-sm bg-gradient-to-br from-amber-500 to-amber-700" />
          <div>
            <div className="label-cap">CVLN</div>
            <div className="font-mono text-xs tracking-widest">META · CVLN <span className="text-amber-400">COMMERCIAL</span></div>
          </div>
        </div>
        <div className="flex items-center gap-6 label-cap">
          <a href="/public" className="hover:text-white">Vitrine publique</a>
          <a href="/audit" className="hover:text-white">Trust chain</a>
          <a href="/login" className="hover:text-white">Login</a>
        </div>
      </div>

      <section className="px-8 py-20 max-w-5xl">
        <div className="label-cap">Commercial ecosystem interface</div>
        <h1 className="text-5xl font-semibold tracking-tight mt-4">
          Transformez vos systèmes <br />
          en <span className="text-amber-400">intelligence opérationnelle</span>.
        </h1>
        <p className="text-base text-white/60 mt-6 max-w-2xl">
          META CVLN apporte la couche d'orchestration, d'intelligence et de confiance
          dont vos systèmes ont besoin. Connexion rapide, orchestration adaptative,
          sécurité éprouvée, notarisation cryptographique.
        </p>
      </section>

      <section className="border-t border-[#252633] px-8 py-16">
        <div className="label-cap mb-6">Nos offres</div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 max-w-6xl">
          {offers.map((o) => (
            <div key={o.name} className="border border-[#252633] rounded-sm p-5 hover:border-amber-500/50 transition-colors">
              <div className="label-cap text-amber-400">{o.name}</div>
              <div className="text-2xl font-mono font-semibold text-white mt-2">{o.price}</div>
              <ul className="text-sm text-white/70 mt-4 space-y-1">
                {o.perks.map((p)=><li key={p}>· {p}</li>)}
              </ul>
              <button data-testid={`offer-${o.name.toLowerCase()}`} className="btn-gold w-full mt-4">Contacter</button>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-[#252633] px-8 py-8 label-cap text-white/40">
        CVLN Group Holding · une plateforme, des possibilités infinies.
      </footer>
    </div>
  );
}
