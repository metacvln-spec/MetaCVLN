export default function MetaPublic() {
  return (
    <div className="min-h-screen bg-[#08090C] text-white" data-testid="meta-public-page">
      <div className="border-b border-[#252633] px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-sm bg-gradient-to-br from-violet-500 to-violet-800" />
          <div>
            <div className="label-cap">CVLN</div>
            <div className="font-mono text-xs tracking-widest">META · CVLN <span className="text-violet-400">PUBLIC</span></div>
          </div>
        </div>
        <div className="flex items-center gap-6 label-cap">
          <a href="/login" className="hover:text-white">Accès interne</a>
          <a href="/commercial" className="hover:text-white">Commercial</a>
          <a href="/audit" className="hover:text-amber-400">Notary audit</a>
        </div>
      </div>

      <section className="px-8 py-24 max-w-5xl">
        <div className="label-cap">Public ecosystem interface</div>
        <h1 className="text-5xl md:text-6xl font-semibold tracking-tight mt-4 leading-none">
          One ecosystem. <br />
          <span className="text-violet-400">Many intelligences.</span>
        </h1>
        <p className="text-base text-white/60 mt-6 max-w-2xl">
          Meta CVLN connecte, comprend, orchestre et sécurise 12 systèmes indépendants
          pour créer une intelligence collective. Chaque événement est notarisé Ed25519,
          vérifiable par un tiers, sans surveillance.
        </p>
        <div className="mt-10 flex gap-3">
          <a href="/audit" className="btn-gold">Voir la trust chain publique</a>
          <a href="#ecosystem" className="btn-ghost">Écosystème CVLN</a>
        </div>
      </section>

      <section id="ecosystem" className="border-t border-[#252633] px-8 py-16">
        <div className="label-cap mb-6">L'écosystème CVLN — 12 entités connectées</div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-6xl">
          {["FREKCORE","FREKANSLA","Agent Factory","Laurent.ia","CVL Academy","Kiltikonet","Gala Cook & Food","Factory Maker Studio","CVLN Wallet","CVLN Command Center","Factory Ops","Production Vault"].map((e)=>(
            <div key={e} className="border border-[#252633] rounded-sm p-4">
              <div className="w-2 h-2 rounded-full bg-emerald-400 mb-3" />
              <div className="text-sm text-white">{e}</div>
              <div className="label-cap mt-1">CONNECTED · notarized</div>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-[#252633] px-8 py-8 label-cap text-white/40">
        CVLN Group · Fondation · OS interne · Commercial · Public — construits ensemble, séparés par doctrine.
      </footer>
    </div>
  );
}
