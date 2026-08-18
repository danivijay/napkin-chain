import { SketchArrow } from '@/components/napkin/Sketch'

const DISCONNECTED = [
  'What is 1B/day in QPS?',
  'How big is a chat message?',
  'What is a typical peak multiplier?',
  'How many QPS per server?',
]

const CHAINED = ['1B req/day', '10K QPS', '30K peak', '~50 servers']

/** The product thesis, drawn: scattered facts versus one carried number. */
export function QuizVsChain() {
  return (
    <div className="grid gap-8 sm:grid-cols-2 sm:gap-10">
      <div>
        <h3 className="text-sm font-semibold text-ink-muted">Disconnected questions</h3>
        <ul className="mt-4 space-y-2.5">
          {DISCONNECTED.map((question, i) => (
            <li
              key={question}
              className="rounded-md border border-dashed border-line bg-subtle/40 px-3.5 py-2.5 text-[13px] text-ink-muted"
              style={{ marginLeft: `${(i % 2) * 14}px` }}
            >
              {question}
            </li>
          ))}
        </ul>
        <p className="mt-4 text-sm leading-relaxed text-ink-secondary">
          You can answer every one of these and still stall on a real system, because
          nothing tells you which number feeds which.
        </p>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-ink">One chain</h3>
        <ol className="mt-4 flex flex-col items-start">
          {CHAINED.map((value, index) => (
            <li key={value} className="flex flex-col items-start">
              <span className="tnum rounded-md border border-good-line bg-good-soft px-3.5 py-2.5 font-mono text-[13px]">
                {value}
              </span>
              {index < CHAINED.length - 1 && <SketchArrow tone="good" className="ml-4 h-6" />}
            </li>
          ))}
        </ol>
        <p className="mt-4 text-sm leading-relaxed text-ink-secondary">
          Errors compound. Being 3× off at step two leaves you 30× off by step six — which
          is exactly the failure interviewers are listening for.
        </p>
      </div>
    </div>
  )
}
