import formulas from '@/data/formulas.json';

/**
 * AI推荐引擎 — 基于症状标签匹配的方剂推荐算法
 * 第一步采用规则匹配，后续接入深度学习模型
 */

// 从四诊数据中提取所有症状标签
export function extractSymptomTags(diagnosis) {
    const tags = new Set();
    const { wangZhen, wenZhen, wenZhenAsk, qieZhen } = diagnosis;

    // 望诊标签 — 从symptoms.json的tag映射
    const wangMap = {
        faceColor: { '面色红赤': ['面赤', '实热'], '面色苍白': ['面色苍白', '血虚', '阳虚'], '面色萎黄': ['面色萎黄', '脾虚'], '面色青紫': ['面色青', '寒证', '瘀血'], '面色晦暗': ['面色晦暗', '肾虚'] },
        tongueColor: { '淡白舌': ['舌淡', '血虚', '气虚'], '红舌': ['舌红', '热证', '阴虚'], '绛舌': ['舌红', '热证'], '紫舌': ['舌暗', '瘀血'], '青舌': ['寒证', '瘀血'] },
        tongueCoating: { '白厚苔': ['苔白腻', '痰湿'], '黄苔': ['苔黄', '热证'], '黄腻苔': ['苔黄腻', '湿热'], '无苔/少苔': ['舌红少苔', '阴虚'], '白滑苔': ['苔白滑', '寒湿'] },
        tongueShape: { '胖大舌': ['气虚', '痰湿'], '瘦薄舌': ['血虚', '阴虚'], '齿痕舌': ['脾虚', '湿'], '裂纹舌': ['阴虚'] },
        bodyType: { '体胖': ['痰湿'], '体瘦': ['阴虚'], '浮肿': ['浮肿', '水湿'] },
        spirit: { '精神疲惫': ['乏力', '气虚'], '烦躁不安': ['烦躁', '热证'], '神志恍惚': ['神疲'] },
    };

    Object.entries(wangMap).forEach(([field, map]) => {
        const val = wangZhen[field];
        if (val && map[val]) map[val].forEach(t => tags.add(t));
    });

    // 闻诊
    const wenMap = {
        voiceType: { '声音低微': ['气虚', '懒言'], '声音嘶哑': ['咽干'], '语声重浊': ['痰湿'] },
        breathType: { '气短': ['气短', '气虚'], '气促': ['喘'], '呼吸深长': ['热证'] },
        coughType: { '干咳少痰': ['咳嗽', '阴虚'], '咳嗽痰多色白': ['咳嗽', '痰多', '痰白', '寒痰'], '咳嗽痰黄稠': ['咳嗽', '痰黄', '热证'], '咳声重浊': ['咳嗽', '痰湿'] },
        bodySmell: { '口臭': ['口臭', '胃热'], '体味重': ['湿热'] },
    };

    Object.entries(wenMap).forEach(([field, map]) => {
        const val = wenZhen[field];
        if (val && map[val]) map[val].forEach(t => tags.add(t));
    });

    // 问诊 — 症状列表
    if (wenZhenAsk.symptoms && Array.isArray(wenZhenAsk.symptoms)) {
        // symptoms is an array of symptom IDs or labels
        const symptomTagMap = {
            '头痛': ['头痛'], '发热': ['发热'], '恶寒': ['恶寒', '寒证'], '失眠': ['失眠'],
            '腹痛': ['腹痛'], '腹胀': ['腹胀'], '恶心呕吐': ['恶心', '呕吐'], '腹泻': ['泄泻', '便溏'],
            '便秘': ['便秘'], '心悸': ['心悸'], '胸闷': ['胸闷'], '头晕': ['头晕', '眩晕'],
            '耳鸣': ['耳鸣'], '目赤': ['目赤'], '咽痛': ['咽痛'], '口干口渴': ['口渴', '口干'],
            '腰膝酸软': ['腰膝酸软'], '关节疼痛': ['关节疼痛'], '四肢冰冷': ['四肢厥冷', '畏寒'],
            '多汗': ['多汗', '自汗'], '盗汗': ['盗汗', '阴虚'], '水肿': ['浮肿'], '月经不调': ['月经不调'],
            '食欲不振': ['食少'], '乏力': ['乏力', '气虚'],
        };
        wenZhenAsk.symptoms.forEach(s => {
            if (symptomTagMap[s]) symptomTagMap[s].forEach(t => tags.add(t));
        });
    }

    // 问诊 — 其他字段
    const askMap = {
        dietPreference: { '喜冷饮': ['热证'], '喜热饮': ['寒证'] },
        sleepQuality: { '入睡困难': ['失眠'], '多梦易醒': ['失眠', '多梦'], '嗜睡': ['嗜睡', '痰湿'] },
        emotionState: { '烦躁易怒': ['烦躁', '急躁', '肝郁'], '情绪低落': ['情志不畅'], '焦虑紧张': ['焦虑'] },
        sweating: { '无汗': ['无汗'], '汗出恶风': ['汗出', '恶风'], '自汗(白天出汗)': ['自汗', '气虚'], '盗汗(夜间出汗)': ['盗汗', '阴虚'], '大汗': ['大汗'] },
        thirst: { '口渴多饮': ['口渴', '热证'], '口干不欲饮': ['口干'], '渴喜热饮': ['寒证'] },
    };
    Object.entries(askMap).forEach(([field, map]) => {
        const val = wenZhenAsk[field];
        if (val && map[val]) map[val].forEach(t => tags.add(t));
    });

    // 切诊 — 脉象
    if (qieZhen.pulseType && Array.isArray(qieZhen.pulseType)) {
        const pulseTagMap = {
            '浮脉': ['脉浮', '表证'], '沉脉': ['脉沉', '里证'], '迟脉': ['脉迟', '寒证'],
            '数脉': ['脉数', '热证'], '滑脉': ['脉滑', '痰湿'], '涩脉': ['脉涩', '瘀血', '血虚'],
            '弦脉': ['脉弦', '肝郁'], '紧脉': ['脉紧', '寒证'], '细脉': ['脉细', '血虚', '阴虚'],
            '洪脉': ['脉洪大', '热证'], '虚脉': ['脉虚', '气虚'], '实脉': ['脉实', '实证'],
            '弱脉': ['脉细弱', '气血虚'], '结脉': ['脉结代', '气滞', '瘀血'], '缓脉': ['脉缓', '湿'],
            '浮缓脉': ['脉浮缓', '表虚'],
        };
        qieZhen.pulseType.forEach(p => {
            if (pulseTagMap[p]) pulseTagMap[p].forEach(t => tags.add(t));
        });
    }

    const strengthMap = { '有力': ['实证'], '无力': ['虚证', '气虚'] };
    if (qieZhen.pulseStrength && strengthMap[qieZhen.pulseStrength]) {
        strengthMap[qieZhen.pulseStrength].forEach(t => tags.add(t));
    }

    return Array.from(tags);
}

// 计算方剂与症状标签的匹配度
function calculateMatchScore(formulaSymptomTags, patientTags) {
    if (!formulaSymptomTags || formulaSymptomTags.length === 0) return 0;
    const matched = formulaSymptomTags.filter(t => patientTags.includes(t));
    const score = matched.length / formulaSymptomTags.length;
    return { score: Math.round(score * 100), matchedTags: matched };
}

// 生成处方修改建议
function generateModifications(formula, patientTags) {
    const modifications = [];
    const modText = formula.modifications || '';

    if (patientTags.includes('气虚') && !formula.composition.some(c => c.herb === '黄芪')) {
        modifications.push({ type: 'add', herb: '黄芪', amount: '15g', reason: '患者气虚明显，加黄芪补气' });
    }
    if (patientTags.includes('阴虚') && !formula.composition.some(c => c.herb === '麦冬')) {
        modifications.push({ type: 'add', herb: '麦冬', amount: '10g', reason: '患者阴虚，加麦冬养阴' });
    }
    if (patientTags.includes('血虚') && !formula.composition.some(c => c.herb === '当归')) {
        modifications.push({ type: 'add', herb: '当归', amount: '10g', reason: '患者血虚，加当归补血' });
    }
    if (patientTags.includes('痰湿') && !formula.composition.some(c => c.herb === '陈皮')) {
        modifications.push({ type: 'add', herb: '陈皮', amount: '6g', reason: '患者痰湿较重，加陈皮理气化痰' });
    }
    if (patientTags.includes('失眠') && !formula.composition.some(c => c.herb === '酸枣仁')) {
        modifications.push({ type: 'add', herb: '酸枣仁', amount: '15g', reason: '患者失眠，加酸枣仁安神' });
    }

    return modifications;
}

// 主推荐函数
export function getRecommendations(diagnosis) {
    const patientTags = extractSymptomTags(diagnosis);

    if (patientTags.length === 0) {
        return { tags: [], recommendations: [] };
    }

    const scored = formulas.map(formula => {
        const { score, matchedTags } = calculateMatchScore(formula.symptomTags, patientTags);
        const modifications = generateModifications(formula, patientTags);
        return {
            ...formula,
            matchScore: score,
            matchedTags,
            suggestedModifications: modifications,
        };
    });

    scored.sort((a, b) => b.matchScore - a.matchScore);

    const top = scored.filter(f => f.matchScore > 0).slice(0, 3);

    return {
        tags: patientTags,
        recommendations: top.map((f, i) => ({
            rank: i + 1,
            id: f.id,
            name: f.name,
            source: f.source,
            author: f.author,
            composition: f.composition,
            indications: f.indications,
            syndrome: f.syndrome,
            matchScore: f.matchScore,
            matchedTags: f.matchedTags,
            modifications: f.modifications,
            suggestedModifications: f.suggestedModifications,
        })),
    };
}
