from app.db.database import engine, Base, SessionLocal
from app.db.models import ModelMetric
from app.ml.evaluate import evaluate_models

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    if db.query(ModelMetric).count() == 0:
        print("Populating model metrics...")
        metrics = evaluate_models("models")
        for m in metrics:
            db_metric = ModelMetric(
                model_name=m['model_name'],
                accuracy=m['accuracy'],
                f1=m['f1'],
                latency=m['latency']
            )
            db.add(db_metric)
        db.commit()
        print("Model metrics populated.")
    else:
        print("Model metrics already exist.")
    db.close()

if __name__ == "__main__":
    init_db()
