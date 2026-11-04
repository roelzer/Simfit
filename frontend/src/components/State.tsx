export function Loading({ text = "Lädt…" }: { text?: string }) {
  return (
    <div className="state" role="status">
      <span className="spinner" aria-hidden="true" />
      {text}
    </div>
  );
}

export function ErrorBox({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="state error" role="alert">
      <strong>Daten konnten nicht geladen werden.</strong>
      <div>{message}</div>
      {onRetry && (
        <div className="row">
          <button onClick={onRetry}>Erneut versuchen</button>
        </div>
      )}
    </div>
  );
}

export function Empty({ text }: { text: string }) {
  return <div className="state">{text}</div>;
}
