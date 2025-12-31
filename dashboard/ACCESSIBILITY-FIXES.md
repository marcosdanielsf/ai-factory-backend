# ♿ Correções de Acessibilidade - Dashboard

**Prioridade:** Média (não afeta funcionamento, mas melhora UX)

---

## ⚠️ Aviso Atual:

```
DialogContent requires a DialogTitle for the component to be accessible
for screen reader users.

If you want to hide the DialogTitle, you can wrap it with our VisuallyHidden component.
```

---

## 🔧 Como Corrigir:

### Opção 1: Adicionar DialogTitle Visível (RECOMENDADO)

Encontre todos os componentes `<DialogContent>` e adicione um `<DialogTitle>`:

```tsx
// ANTES (sem título)
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <p>Content here</p>
  </DialogContent>
</Dialog>

// DEPOIS (com título visível)
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <DialogTitle>Dialog Title</DialogTitle>
    <p>Content here</p>
  </DialogContent>
</Dialog>
```

### Opção 2: DialogTitle Oculto (se não quiser mostrar)

Se você não quer um título visível mas quer manter acessibilidade:

```tsx
import { VisuallyHidden } from '@radix-ui/react-visually-hidden'

<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <VisuallyHidden>
      <DialogTitle>Screen reader only title</DialogTitle>
    </VisuallyHidden>
    <p>Content here</p>
  </DialogContent>
</Dialog>
```

---

## 📁 Arquivos Prováveis a Verificar:

Procure por `DialogContent` nos seguintes arquivos:

```bash
# Buscar em todos os componentes
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/dashboard
grep -r "DialogContent" app/ components/ --include="*.tsx" --include="*.jsx"
```

Arquivos comuns:
- `components/ui/dialog.tsx` (componente base)
- `app/(dashboard)/**/*.tsx` (páginas do dashboard)
- Qualquer modal ou popup no app

---

## 🧪 Como Testar:

1. Abra o console do navegador (F12)
2. Navegue pelo dashboard
3. Abra qualquer modal/dialog
4. Verifique se o aviso desapareceu

---

## 📊 Impacto:

**Funcionalidade:** ✅ Não afetada
**SEO:** ✅ Não afetado
**Acessibilidade:** ⚠️ Prejudicada (leitores de tela)
**Auditoria Lighthouse:** 📉 Pode reduzir score de acessibilidade

---

## 🎯 Quando Corrigir:

- ✅ **Agora:** Se você planeja lançar para usuários reais em breve
- 📅 **Depois:** Se está apenas testando funcionalidades
- 🚀 **Antes de Produção:** OBRIGATÓRIO para compliance de acessibilidade (WCAG 2.1)

---

## 📚 Referência:

- [Radix UI Dialog Docs](https://radix-ui.com/primitives/docs/components/dialog)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [VisuallyHidden Component](https://radix-ui.com/primitives/docs/utilities/visually-hidden)

---

**Status:** ⚠️ Avisos de acessibilidade presentes (não crítico)
**Prioridade:** Média
**Tempo estimado:** 5-10 minutos por dialog

---

**Nota:** O sistema está 100% funcional. Esta correção é apenas para melhorar a experiência de usuários com deficiências visuais.
