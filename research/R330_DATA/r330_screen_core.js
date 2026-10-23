function runR330Screen(rawCsvBySymbol) {
  const universe = [
    { symbol: "AAPL", assetClass: "stock" },
    { symbol: "AMZN", assetClass: "stock" },
    { symbol: "GOOG", assetClass: "stock" },
    { symbol: "MSFT", assetClass: "stock" },
    { symbol: "NVDA", assetClass: "stock" },
    { symbol: "TSLA", assetClass: "stock" },
    { symbol: "AMD", assetClass: "stock" },
    { symbol: "META", assetClass: "stock" },
    { symbol: "BTCUSD", assetClass: "crypto" },
    { symbol: "ETHUSD", assetClass: "crypto" }
  ];
  const startDate = "2024-10-23";
  const endDate = "2026-10-22";
  const discoveryEnd = "2025-10-22";
  const confirmationStart = "2025-10-23";
  const root20 = Math.sqrt(20);
  const summaryInfo = [];
  const parsed = {};
  function dateInZone(ts, timeZone) {
    const parts = new Intl.DateTimeFormat("en-US", {
      timeZone,
      year: "numeric",
      month: "2-digit",
      day: "2-digit"
    }).formatToParts(new Date(ts));
    const p = {};
    for (const q of parts) if (q.type !== "literal") p[q.type] = q.value;
    return p.year + "-" + p.month + "-" + p.day;
  }
  function addDays(label, days) {
    return new Date(Date.parse(label + "T00:00:00Z") + days * 86400000).toISOString().slice(0, 10);
  }
  function parseCsv(symbol, csv, assetClass) {
    const lines = csv.trimEnd().split(/\r?\n/);
    if (lines.length < 3 || lines[0] !== "v,vw,o,c,h,l,t,n") {
      throw new Error("DATA_HEADER_OR_LENGTH:" + symbol);
    }
    const rows = [];
    const seen = new Set();
    for (let lineNo = 1; lineNo < lines.length; lineNo++) {
      const fields = lines[lineNo].split(",");
      if (fields.length !== 8) throw new Error("DATA_COLUMN_COUNT:" + symbol + ":" + lineNo);
      const row = {
        volume: Number(fields[0]),
        vwap: Number(fields[1]),
        open: Number(fields[2]),
        close: Number(fields[3]),
        high: Number(fields[4]),
        low: Number(fields[5]),
        ts: Number(fields[6]),
        trades: Number(fields[7])
      };
      if (!Number.isFinite(row.ts) || !Number.isFinite(row.close) || row.close <= 0 ||
          !Number.isFinite(row.open) || !Number.isFinite(row.high) || !Number.isFinite(row.low) ||
          row.high < Math.max(row.open, row.close, row.low) ||
          row.low > Math.min(row.open, row.close, row.high)) {
        throw new Error("DATA_INVALID_OHLC:" + symbol + ":" + lineNo);
      }
      row.date = assetClass === "stock"
        ? dateInZone(row.ts, "America/New_York")
        : new Date(row.ts).toISOString().slice(0, 10);
      if (seen.has(row.date)) throw new Error("DATA_DUPLICATE_DATE:" + symbol + ":" + row.date);
      seen.add(row.date);
      rows.push(row);
    }
    rows.sort((a, b) => a.ts - b.ts);
    for (let i = 1; i < rows.length; i++) {
      if (rows[i].ts <= rows[i - 1].ts || rows[i].date <= rows[i - 1].date) {
        throw new Error("DATA_NOT_STRICTLY_SORTED:" + symbol);
      }
    }
    const labels = new Map();
    for (let i = 0; i < rows.length; i++) labels.set(rows[i].date, i);
    return { rows, labels };
  }
  for (const ins of universe) {
    if (typeof rawCsvBySymbol[ins.symbol] !== "string") throw new Error("MISSING_INPUT:" + ins.symbol);
    parsed[ins.symbol] = parseCsv(ins.symbol, rawCsvBySymbol[ins.symbol], ins.assetClass);
    const arr = parsed[ins.symbol].rows;
    summaryInfo.push({
      symbol: ins.symbol,
      assetClass: ins.assetClass,
      rowCount: arr.length,
      firstDate: arr[0].date,
      lastDate: arr[arr.length - 1].date
    });
  }
  function signalAt(ins, snapshotDate) {
    const df = parsed[ins.symbol];
    let idx = -1;
    for (let i = df.rows.length - 1; i >= 0; i--) {
      if (df.rows[i].date <= snapshotDate) {
        idx = i;
        break;
      }
    }
    if (idx < 20) {
      return {
        symbol: ins.symbol, assetClass: ins.assetClass, signalDate: snapshotDate,
        closeDate: idx >= 0 ? df.rows[idx].date : null,
        close: idx >= 0 ? df.rows[idx].close : null,
        mom20: null, sdDaily: null, vol20: null, score: null,
        direction: 0, invVol: 0, weight: 0
      };
    }
    const closes = df.rows;
    const current = closes[idx].close;
    const mom20 = current / closes[idx - 20].close - 1;
    const rs = [];
    for (let j = idx - 19; j <= idx; j++) {
      const prior = closes[j - 1].close;
      const now = closes[j].close;
      rs.push(now / prior - 1);
    }
    const mean = rs.reduce((a, b) => a + b, 0) / rs.length;
    const sd2 = rs.reduce((a, r) => a + (r - mean) * (r - mean), 0) / rs.length;
    const sdDaily = Math.sqrt(Math.max(0, sd2));
    const vol20 = sdDaily * root20;
    const score = vol20 > 0 ? mom20 / vol20 : null;
    const direction = score !== null && score >= 1 ? 1 : score !== null && score <= -1 ? -1 : 0;
    return {
      symbol: ins.symbol, assetClass: ins.assetClass, signalDate: snapshotDate,
      closeDate: closes[idx].date, close: current,
      mom20, sdDaily, vol20, score, direction,
      invVol: direction !== 0 && sdDaily > 0 ? 1 / sdDaily : 0,
      weight: 0
    };
  }
  function forwardAt(ins, snapshotDate) {
    const df = parsed[ins.symbol];
    const lo = addDays(snapshotDate, 6);
    const hi = addDays(snapshotDate, 7);
    let chosen = null;
    for (let i = 0; i < df.rows.length; i++) {
      const row = df.rows[i];
      if (row.date >= lo && row.date <= hi && row.date <= endDate) {
        if (chosen === null || row.date > chosen.date) chosen = row;
      }
    }
    return chosen ? { date: chosen.date, close: chosen.close } : null;
  }
  const snapshots = [];
  for (let day = startDate; day <= endDate; day = addDays(day, 1)) {
    const dow = new Date(day + "T00:00:00Z").getUTCDay();
    if (dow !== 5) continue;
    const sigs = universe.map(ins => signalAt(ins, day));
    const invSum = sigs.reduce((s, x) => s + x.invVol, 0);
    for (const sig of sigs) sig.weight = invSum > 0 ? sig.direction * sig.invVol / invSum : 0;
    const forwards = {};
    let maxForwardDate = null;
    for (const ins of universe) {
      const f = forwardAt(ins, day);
      forwards[ins.symbol] = f;
      if (f && (maxForwardDate === null || f.date > maxForwardDate)) maxForwardDate = f.date;
    }
    snapshots.push({ signalDate: day, signals: sigs, forwards, maxForwardDate });
  }
  function median(values) {
    if (!values.length) return null;
    const s = values.slice().sort((a, b) => a - b);
    const mid = Math.floor(s.length / 2);
    return s.length % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2;
  }
  function bootstrapMeanCI(values, reps, blockLength, seedNum) {
    if (values.length < blockLength) {
      return { reps, blockLength, seedInput: seedNum, seedUint32: seedNum >>> 0, low: null, high: null };
    }
    let state = seedNum >>> 0;
    if (state === 0) state = 2463534242;
    function rand() {
      state ^= state << 13;
      state ^= state >>> 17;
      state ^= state << 5;
      state >>>= 0;
      return state / 4294967296;
    }
    const n = values.length;
    const means = new Array(reps);
    for (let b = 0; b < reps; b++) {
      let total = 0;
      let count = 0;
      while (count < n) {
        const blockStart = Math.floor(rand() * n);
        for (let k = 0; k < blockLength && count < n; k++) {
          total += values[(blockStart + k) % n];
          count++;
        }
      }
      means[b] = total / n;
    }
    means.sort((a, b) => a - b);
    return {
      reps, blockLength, seedInput: seedNum, seedUint32: seedNum >>> 0,
      low: means[Math.floor(0.025 * (reps - 1))],
      high: means[Math.floor(0.975 * (reps - 1))]
    };
  }
  function scorePartition(name, startLabel, endLabel) {
    const eligible = snapshots.filter(s => {
      if (s.signalDate < startLabel || s.signalDate > endLabel || !s.maxForwardDate) return false;
      if (name === "discovery") return s.maxForwardDate <= discoveryEnd;
      return s.signalDate >= confirmationStart && s.maxForwardDate <= endDate;
    });
    let prevWeights = Object.fromEntries(universe.map(x => [x.symbol, 0]));
    const weeklyRows = [];
    const assetRows = [];
    for (let si = 0; si < eligible.length; si++) {
      const s = eligible[si];
      let gross = 0, commission = 0, primaryExtra = 0, stressExtra = 0, turnover = 0;
      const currentWeights = {};
      const rowCosts = {};
      for (const ins of universe) {
        const sig = s.signals.find(x => x.symbol === ins.symbol);
        const target = sig.weight;
        currentWeights[ins.symbol] = target;
        const delta = Math.abs(target - prevWeights[ins.symbol]);
        const f = s.forwards[ins.symbol];
        if (target !== 0 && !f) {
          throw new Error("DATA_ACTIVE_POSITION_WITHOUT_FORWARD:" + name + ":" + s.signalDate + ":" + ins.symbol);
        }
        const fwdReturn = f && sig.close > 0 ? f.close / sig.close - 1 : null;
        const grossContribution = target !== 0 && fwdReturn !== null ? target * fwdReturn : 0;
        const commRate = ins.assetClass === "stock" ? 0.00004 : 0.0004;
        const priRate = ins.assetClass === "stock" ? 0.0005 : 0.0015;
        const stressRate = ins.assetClass === "stock" ? 0.001 : 0.003;
        const commCost = delta * commRate;
        const priCost = delta * priRate;
        const stressCost = delta * stressRate;
        gross += grossContribution;
        commission += commCost;
        primaryExtra += priCost;
        stressExtra += stressCost;
        turnover += delta;
        rowCosts[ins.symbol] = { commission: commCost, primaryExtra: priCost, stressExtra: stressCost };
        assetRows.push({
          partition: name, signalDate: s.signalDate, exitDate: f ? f.date : null,
          symbol: ins.symbol, assetClass: ins.assetClass,
          signalCloseDate: sig.closeDate, signalClose: sig.close,
          mom20: sig.mom20, sdDaily: sig.sdDaily, vol20: sig.vol20,
          score: sig.score, direction: sig.direction, targetWeight: target,
          forwardClose: f ? f.close : null, forwardReturn: fwdReturn,
          grossContribution, turnover: delta, commissionCost: commCost,
          primaryExtraCost: priCost, stressExtraCost: stressCost
        });
      }
      const primaryNet = gross - commission - primaryExtra;
      const stressNet = gross - commission - stressExtra;
      weeklyRows.push({
        partition: name, signalDate: s.signalDate, exitHorizonEndDate: s.maxForwardDate,
        grossReturn: gross, commissionOnlyReturn: gross - commission,
        primaryExtraCost: primaryExtra, stressExtraCost: stressExtra, commissionCost: commission,
        primaryNetReturn: primaryNet, stressNetReturn: stressNet,
        turnover, targetGrossExposure: Object.values(currentWeights).reduce((a, x) => a + Math.abs(x), 0),
        weights: currentWeights
      });
      prevWeights = currentWeights;
    }
    if (weeklyRows.length > 0) {
      const last = weeklyRows[weeklyRows.length - 1];
      let exitTurnover = 0, exitComm = 0, exitPrimary = 0, exitStress = 0;
      for (const ins of universe) {
        const amount = Math.abs(prevWeights[ins.symbol]);
        const commRate = ins.assetClass === "stock" ? 0.00004 : 0.0004;
        const priRate = ins.assetClass === "stock" ? 0.0005 : 0.0015;
        const stressRate = ins.assetClass === "stock" ? 0.001 : 0.003;
        exitTurnover += amount;
        exitComm += amount * commRate;
        exitPrimary += amount * priRate;
        exitStress += amount * stressRate;
        const ar = assetRows.findLast ? assetRows.findLast(x => x.partition === name && x.signalDate === last.signalDate && x.symbol === ins.symbol) : null;
        if (ar) {
          ar.turnover += amount;
          ar.commissionCost += amount * commRate;
          ar.primaryExtraCost += amount * priRate;
          ar.stressExtraCost += amount * stressRate;
        }
      }
      last.turnover += exitTurnover;
      last.commissionCost += exitComm;
      last.primaryExtraCost += exitPrimary;
      last.stressExtraCost += exitStress;
      last.commissionOnlyReturn -= exitComm;
      last.primaryNetReturn -= exitComm + exitPrimary;
      last.stressNetReturn -= exitComm + exitStress;
      last.exitTurnover = exitTurnover;
    }
    const arr = weeklyRows.map(x => x.primaryNetReturn);
    const stressArr = weeklyRows.map(x => x.stressNetReturn);
    const grossArr = weeklyRows.map(x => x.grossReturn);
    let equityPrimary = 1, equityStress = 1, peak = 1, maxDD = 0;
    for (const x of arr) {
      equityPrimary *= 1 + x;
      peak = Math.max(peak, equityPrimary);
      maxDD = Math.min(maxDD, equityPrimary / peak - 1);
    }
    for (const x of stressArr) equityStress *= 1 + x;
    const mean = arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : null;
    const variance = arr.length ? arr.reduce((a, b) => a + (b - mean) * (b - mean), 0) / arr.length : null;
    const sd = variance !== null ? Math.sqrt(variance) : null;
    const positives = arr.filter(x => x > 0).reduce((a, b) => a + b, 0);
    const negatives = arr.filter(x => x < 0).reduce((a, b) => a - b, 0);
    const sharpe = sd > 0 ? Math.sqrt(52) * mean / sd : null;
    const pf = negatives > 0 ? positives / negatives : null;
    const grossSum = grossArr.reduce((a, b) => a + b, 0);
    const commOnlySum = weeklyRows.reduce((a, x) => a + x.commissionOnlyReturn, 0);
    const totalComm = weeklyRows.reduce((a, x) => a + x.commissionCost, 0);
    const totalPrimaryExtra = weeklyRows.reduce((a, x) => a + x.primaryExtraCost, 0);
    const totalStressExtra = weeklyRows.reduce((a, x) => a + x.stressExtraCost, 0);
    const totalTurnover = weeklyRows.reduce((a, x) => a + x.turnover, 0);
    const ci = bootstrapMeanCI(arr, 10000, 4, 33020261023);
    const perAsset = universe.map(ins => {
      const rows = assetRows.filter(x => x.symbol === ins.symbol);
      return {
        symbol: ins.symbol, assetClass: ins.assetClass,
        grossContribution: rows.reduce((a, x) => a + x.grossContribution, 0),
        turnover: rows.reduce((a, x) => a + x.turnover, 0),
        commissionCost: rows.reduce((a, x) => a + x.commissionCost, 0),
        primaryExtraCost: rows.reduce((a, x) => a + x.primaryExtraCost, 0),
        stressExtraCost: rows.reduce((a, x) => a + x.stressExtraCost, 0),
        activeWeeks: rows.filter(x => x.targetWeight !== 0).length
      };
    });
    return {
      partition: name,
      eligibleWeeks: weeklyRows.length,
      signalStart: weeklyRows.length ? weeklyRows[0].signalDate : null,
      signalEnd: weeklyRows.length ? weeklyRows[weeklyRows.length - 1].signalDate : null,
      cumulativePrimaryNetReturn: equityPrimary - 1,
      cumulativeStressNetReturn: equityStress - 1,
      arithmeticSumGrossReturn: grossSum,
      arithmeticSumCommissionOnlyReturn: commOnlySum,
      commissionCost: totalComm,
      primaryExtraCost: totalPrimaryExtra,
      stressExtraCost: totalStressExtra,
      meanPrimaryNetWeeklyReturn: mean,
      medianPrimaryNetWeeklyReturn: median(arr),
      winWeekRate: arr.length ? arr.filter(x => x > 0).length / arr.length : null,
      profitFactorWeekly: pf,
      maxDrawdownPrimary: maxDD,
      annualizedWeeklySharpe: sharpe,
      totalTurnover: totalTurnover,
      bootstrapMeanPrimary95: ci,
      perAsset,
      weeklyRows,
      assetRows
    };
  }
  const discovery = scorePartition("discovery", startDate, discoveryEnd);
  const confirmation = scorePartition("confirmation", confirmationStart, endDate);
  const dataAudit = {
    instruments: summaryInfo,
    rawHeadersChecked: true,
    duplicateDates: 0,
    invalidOHLC: 0,
    weeklySnapshotCount: snapshots.length,
    snapshotStart: snapshots.length ? snapshots[0].signalDate : null,
    snapshotEnd: snapshots.length ? snapshots[snapshots.length - 1].signalDate : null
  };
  const pass = discovery.cumulativePrimaryNetReturn > 0 &&
    confirmation.cumulativePrimaryNetReturn > 0 &&
    confirmation.bootstrapMeanPrimary95.low > 0 &&
    confirmation.cumulativeStressNetReturn > 0;
  return {
    experiment: "R330",
    claimType: "initial screen only; not funded-ready",
    universe: universe,
    dates: { start: startDate, end: endDate, discoveryForwardCutoff: discoveryEnd, confirmationStart, confirmationForwardCutoff: endDate },
    frozenSignal: { lookbackBars: 20, scoreThreshold: 1, rebalance: "weekly Friday snapshot", grossExposureCap: 1 },
    costAssumptions: { stockCommissionPerSide: 0.00004, cryptoCommissionPerSide: 0.0004, stockExtraPerSideBps: { floor: 0, primary: 5, stress: 10 }, cryptoExtraPerSideBps: { floor: 0, primary: 15, stress: 30 } },
    verdict: pass ? "PASS — SCREEN ONLY" : "GAGAL — ECONOMIC SCREEN",
    promotionNote: "Underlying-market daily aggregates are not exact FundedNext CFD BID/ASK quotes; no swap deduction or five-minute fill is modeled. This verdict cannot establish funded readiness or day-179 pass probability.",
    dataAudit,
    discovery,
    confirmation
  };
}
