"""
测试预测脚本
"""
import sys
sys.path.insert(0, '.')

from predictor import TCMFormulaPredictor

def main():
    print("=" * 60)
    print("  中医方剂推荐系统 - 预测测试")
    print("=" * 60)
    
    print("\n正在加载模型...")
    predictor = TCMFormulaPredictor(
        model_path='../training/checkpoints/best_model.pt',
        vocab_dir='../training/data'
    )
    
    print("\n" + "-" * 60)
    print("  测试案例")
    print("-" * 60)
    
    test_cases = [
        {
            "name": "麻黄汤证",
            "symptoms": ["恶寒", "发热", "无汗", "头痛", "身痛", "喘"],
            "expected": "麻黄汤"
        },
        {
            "name": "桂枝汤证",
            "symptoms": ["发热", "恶风", "汗出", "头痛"],
            "expected": "桂枝汤"
        },
        {
            "name": "四君子汤证",
            "symptoms": ["气短", "乏力", "面色萎黄", "食欲不振"],
            "expected": "四君子汤"
        },
        {
            "name": "小柴胡汤证",
            "symptoms": ["寒热往来", "胸胁苦满", "口苦", "咽干", "目眩"],
            "expected": "小柴胡汤"
        },
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n【案例 {i}】{case['name']}")
        print(f"  症状: {', '.join(case['symptoms'])}")
        print(f"  预期方剂: {case['expected']}")
        
        result = predictor.predict(case['symptoms'])
        
        print(f"  预测药材:")
        for herb in result['herbs']:
            print(f"    - {herb['name']}: {herb['probability']:.2%}")
    
    print("\n" + "=" * 60)
    print("  测试完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
