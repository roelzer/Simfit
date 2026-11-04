from sqlmodel import Session, select

from .models import Food, NutritionGoal

# name, kcal, protein, carbs, fat (pro 100 g)
FOODS = [
    ("Haferflocken", 372, 13.5, 59, 7), ("Vollkornbrot", 220, 8, 41, 1.5), ("Weißbrot", 265, 8, 50, 3),
    ("Reis, gekocht", 130, 2.7, 28, 0.3), ("Nudeln, gekocht", 158, 5.8, 31, 0.9), ("Kartoffeln, gekocht", 86, 2, 20, 0.1),
    ("Hähnchenbrust, roh", 110, 23, 0, 1.5), ("Rindfleisch, mager", 150, 21, 0, 7), ("Lachs", 208, 20, 0, 13),
    ("Thunfisch (Dose, Wasser)", 116, 26, 0, 1), ("Ei (Hühnerei)", 143, 12.6, 0.7, 9.9), ("Magerquark", 67, 12, 4, 0.3),
    ("Naturjoghurt 1,5%", 47, 4, 4.5, 1.5), ("Milch 1,5%", 47, 3.4, 4.9, 1.5), ("Gouda", 356, 25, 0, 28),
    ("Banane", 89, 1.1, 23, 0.3), ("Apfel", 52, 0.3, 14, 0.2), ("Beeren, gemischt", 45, 0.8, 9, 0.4),
    ("Brokkoli", 34, 2.8, 7, 0.4), ("Tomate", 18, 0.9, 3.9, 0.2), ("Gurke", 15, 0.7, 3.6, 0.1),
    ("Karotte", 41, 0.9, 10, 0.2), ("Avocado", 160, 2, 9, 15), ("Olivenöl", 884, 0, 0, 100),
    ("Erdnussbutter", 588, 25, 20, 50), ("Mandeln", 579, 21, 22, 50), ("Linsen, gekocht", 116, 9, 20, 0.4),
    ("Tofu", 76, 8, 1.9, 4.8), ("Whey-Protein-Pulver", 380, 78, 6, 5), ("Schokolade, Vollmilch", 535, 7.6, 59, 30),
]


def seed(s: Session) -> None:
    if not s.exec(select(Food).limit(1)).first():
        s.add_all(Food(name=n, kcal_100g=k, protein_100g=p, carbs_100g=c, fat_100g=f) for n, k, p, c, f in FOODS)
    if not s.get(NutritionGoal, 1):
        s.add(NutritionGoal())
    s.commit()
