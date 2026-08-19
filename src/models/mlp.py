import numpy as np
import tensorflow as tf

from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import f1_score

class MacroF1Callback(tf.keras.callbacks.Callback):

    def __init__(
        self,
        X_val,
        y_val,
        n_classes,
    ):
        super().__init__()

        self.X_val = X_val
        self.y_val = y_val
        self.n_classes = n_classes

    def on_epoch_end(self, epoch, logs=None):

        logs = logs or {}

        y_prob = self.model.predict(
            self.X_val,
            verbose=0,
        )

        if self.n_classes == 2:
            y_pred = (
                y_prob.ravel() >= 0.5
            ).astype(int)

        else:
            y_pred = np.argmax(
                y_prob,
                axis=1,
            )

        macro_f1 = f1_score(
            self.y_val,
            y_pred,
            average="macro",
        )

        logs["val_macro_f1"] = macro_f1

        print(
            f" - val_macro_f1: {macro_f1:.4f}",
            end="",
        )

def get_class_weights(y):
    classes = np.unique(y)

    weights = compute_class_weight(
        class_weight="balanced",
        classes=classes,
        y=y,
    )

    return {
        int(cls): float(weight)
        for cls, weight in zip(classes, weights)
    }


def build_mlp(
    input_dim,
    n_classes,
    random_state=42,
):
    tf.keras.backend.clear_session()
    tf.random.set_seed(random_state)

    model = tf.keras.Sequential([
        tf.keras.layers.Input(
            shape=(input_dim,)
        ),
        tf.keras.layers.Dense(
            64,
            activation="relu",
        ),
        tf.keras.layers.Dense(
            32,
            activation="relu",
        ),
    ])

    if n_classes == 2:
        model.add(
            tf.keras.layers.Dense(
                1,
                activation="sigmoid",
            )
        )

        loss = "binary_crossentropy"

    else:
        model.add(
            tf.keras.layers.Dense(
                n_classes,
                activation="softmax",
            )
        )

        loss = "sparse_categorical_crossentropy"

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=1e-3
        ),
        loss=loss,
    )

    return model


def train_mlp(
    model,
    X_train,
    y_train,
    X_val,
    y_val,
    class_weight,
    n_classes,
    epochs=100,
    batch_size=256,
):

    macro_f1_callback = MacroF1Callback(
        X_val=X_val,
        y_val=y_val,
        n_classes=n_classes,
    )

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_macro_f1",
        mode="max",
        patience=10,
        restore_best_weights=True,
        verbose=1,
    )

    history = model.fit(
        X_train,
        y_train,
        validation_data=(
            X_val,
            y_val,
        ),
        epochs=epochs,
        batch_size=batch_size,
        class_weight=class_weight,
        callbacks=[
            macro_f1_callback,
            early_stopping,
        ],
        verbose=1,
    )

    return history